"""Compress chat history so multi-turn context survives the small_llm budget.

Previously the rewrite/router prompt did ``chat_history[-3:]`` and threw
older turns away. In practice, troubleshooting conversations regularly
exceed 5 turns, and the dropped context contains exactly the info that
matters next ("user already tried X, ruled out Y").

This module keeps the most recent ``recent_n`` turns RAW and runs older
turns through a single small_llm summarization call. The summary is
designed to preserve:

  - what the user is trying to do (overall goal)
  - confirmed observations / measurements
  - approaches the user has already tried and ruled out
  - decisions the user has already made

It deliberately discards the assistant's verbose explanations — those
were already used by the user and don't need to live in the prompt
forever.

Hash-keyed caching keeps the summarization cost amortized: same older
turns produce the same summary, so a 7-turn chat only pays for one
summarization call total (not one per turn after #4).
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, List, Tuple

from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


# Process-local cache. Key = hash of old turns; value = summary string.
# Bounded to avoid unbounded growth in long-running processes; the access
# pattern is a series of growing-prefix hashes so a small cap is enough.
_SUMMARY_CACHE: Dict[str, str] = {}
_SUMMARY_CACHE_MAX = 64


def _turn_text(turn: Dict[str, Any]) -> Tuple[str, str]:
    """Pull (user_msg, assistant_msg) out of a chat-history turn dict."""
    user = str(turn.get("user") or "").strip()
    assistant = str(turn.get("assistant") or "").strip()
    return user, assistant


def _hash_turns(turns: List[Dict[str, Any]]) -> str:
    """Stable hash of the older-turns content for cache lookup."""
    payload = json.dumps(
        [(_turn_text(t)) for t in turns], ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()  # noqa: S324  (cache key only)


def _evict_if_needed() -> None:
    if len(_SUMMARY_CACHE) <= _SUMMARY_CACHE_MAX:
        return
    # Drop ~25% of the cache (oldest by insertion order in Python 3.7+).
    drop = max(1, _SUMMARY_CACHE_MAX // 4)
    for k in list(_SUMMARY_CACHE.keys())[:drop]:
        _SUMMARY_CACHE.pop(k, None)


def _summarize_turns(turns: List[Dict[str, Any]], small_llm: Any) -> str:
    """Compress N (user, assistant) pairs into a 4-8 bullet history block.

    Returns "" on any failure (cache key NOT written, so a transient API
    error doesn't poison subsequent calls).
    """
    if not turns or small_llm is None:
        return ""

    # Cap input size — even at 5KB per turn, 10 turns is 50KB which fits qwen-flash.
    # Beyond that, the summary itself loses focus.
    capped_turns = turns[-15:] if len(turns) > 15 else turns

    rendered = []
    for i, turn in enumerate(capped_turns, start=1):
        u, a = _turn_text(turn)
        # Truncate assistant answers — we only need the gist, not the full prose.
        if len(a) > 600:
            a = a[:600] + " […truncated…]"
        rendered.append(f"Turn {i}\nUser: {u}\nAssistant: {a}")
    transcript = "\n\n".join(rendered)

    prompt = f"""You are summarizing the EARLIER part of an ongoing biomedical
research conversation. The next message in the conversation will use your
summary as context, so capture only what the user genuinely needs the
assistant to remember going forward.

Summarize the following turns into 4-8 bullets covering:
- The user's overall goal / experimental setup
- Specific numbers / observations / measurements they have stated
- Approaches the user has TRIED or RULED OUT
- Decisions / preferences the user has already locked in

Do NOT summarize the assistant's reasoning or full explanations — those
are spent. Be concrete: keep proper nouns, reagent names, numeric values
verbatim. Drop pleasantries.

Earlier turns:
{transcript}

Output: ONLY the bullet list (no preamble, no closing line). Use "- " bullets."""

    try:
        resp = small_llm.invoke([HumanMessage(content=prompt)])
        text = resp.content.strip() if hasattr(resp, "content") else str(resp).strip()
    except Exception:
        logger.warning("History summarization failed; falling back to raw last-3 turns.", exc_info=True)
        return ""

    # Strip code fences in case the model decorated the output.
    if text.startswith("```"):
        text = text.split("```", 2)[1].lstrip("\n")
        if text.endswith("```"):
            text = text[: text.rfind("```")].rstrip()
    return text.strip()


def render_compressed_history(
    chat_history: List[Dict[str, Any]],
    small_llm: Any = None,
    recent_n: int = 3,
) -> str:
    """Return a single ``"Previous conversation:..."`` block for prompts.

    Format::

        Previous conversation:
        [Earlier conversation summary]
        - Goal: ...
        - Already tried: ...
        - Confirmed observation: ...

        [Recent turns - verbatim]
        User: ...
        Assistant: ...
        ...

    Returns empty string when ``chat_history`` is empty. Falls back to the
    legacy ``chat_history[-recent_n:]`` rendering when ``small_llm`` is
    None or summarization fails.
    """
    if not chat_history:
        return ""

    if len(chat_history) <= recent_n or small_llm is None:
        # Cheap path: legacy behavior. Short conversations never pay the
        # summarization cost.
        recent = chat_history[-recent_n:] if len(chat_history) > recent_n else list(chat_history)
        rendered = "\n".join(
            f"User: {turn.get('user', '')}\nAssistant: {turn.get('assistant', '')}"
            for turn in recent
        )
        return f"Previous conversation:\n{rendered}\n\n"

    # Hot path: split into older + recent, summarize older, attach recent raw.
    older = chat_history[:-recent_n]
    recent = chat_history[-recent_n:]

    cache_key = _hash_turns(older)
    summary = _SUMMARY_CACHE.get(cache_key)
    if summary is None:
        summary = _summarize_turns(older, small_llm)
        if summary:
            _SUMMARY_CACHE[cache_key] = summary
            _evict_if_needed()
        else:
            # Fallback: use raw older turns trimmed (better than nothing).
            summary = "\n".join(
                f"- Turn {i}: user asked about \"{(_turn_text(t)[0] or '')[:100]}\""
                for i, t in enumerate(older, start=1)
            )

    recent_rendered = "\n".join(
        f"User: {turn.get('user', '')}\nAssistant: {turn.get('assistant', '')}"
        for turn in recent
    )
    return (
        "Previous conversation:\n"
        f"[Earlier conversation summary — {len(older)} turn(s) compressed]\n"
        f"{summary}\n\n"
        f"[Recent turns — verbatim]\n"
        f"{recent_rendered}\n\n"
    )
