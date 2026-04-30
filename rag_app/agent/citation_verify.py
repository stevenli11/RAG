"""Post-generation citation faithfulness verifier.

After the answer LLM finishes, we re-check each ``[N]`` citation by asking a
small_llm whether the abstract actually supports the claim sentence. The cost
is one extra small_llm call (~1-1.5s on qwen-flash) for the whole answer,
batched by passing every (claim, abstract) pair in a single JSON-mode prompt.

This catches the common failure mode where the answer LLM cites an abstract
that's topically related but doesn't actually support the specific claim — a
hallucination class that pure prompt engineering can't reliably prevent.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


# Match `[N]`, `[N, M]`, `[N, M, K]` — same shape as linkify_citations expects.
_CITE_RE = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


def _claim_window(text: str, start: int, end: int) -> str:
    """Extract the sentence-like span surrounding a citation marker.

    Walks left to the previous sentence terminator / line break, then right to
    the next one. Strips the citation marker itself out of the returned
    string so the verifier judges the claim, not the marker.
    """
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start), text.rfind("!", 0, start), text.rfind("?", 0, start))
    if left < 0:
        left = 0
    right_candidates = [
        idx for idx in (
            text.find(".", end),
            text.find("\n", end),
            text.find("!", end),
            text.find("?", end),
        ) if idx >= 0
    ]
    right = min(right_candidates) if right_candidates else len(text)
    window = text[left:right + 1].strip(" .!?\n\t")
    # Strip the inline `[N]` markers so the verifier reads the claim cleanly.
    window = _CITE_RE.sub("", window).strip()
    # Collapse whitespace.
    return re.sub(r"\s+", " ", window)


def _extract_pairs(answer: str, max_ref: int) -> List[Dict[str, Any]]:
    """Return list of {claim, ref_n} pairs from inline `[N]` citations."""
    pairs: List[Dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for m in _CITE_RE.finditer(answer):
        nums_raw = m.group(1)
        try:
            nums = [int(x.strip()) for x in nums_raw.split(",")]
        except ValueError:
            continue
        claim = _claim_window(answer, m.start(), m.end())
        if not claim or len(claim) < 12:
            continue
        for n in nums:
            if n < 1 or n > max_ref:
                continue
            key = (claim[:200], n)
            if key in seen:
                continue
            seen.add(key)
            pairs.append({"claim": claim[:400], "ref_n": n})
    return pairs


def _ref_excerpt(article: Dict[str, Any], max_chars: int = 600) -> str:
    title = str(article.get("title") or "")
    abstract = str(article.get("abstract") or "")
    text = f"{title}. {abstract}".strip()
    return text[:max_chars]


def verify_citations(
    *,
    answer: str,
    references_used: List[Dict[str, Any]],
    references_all: List[Dict[str, Any]],
    small_llm: Any,
) -> List[Dict[str, Any]]:
    """Return per-citation verdict list.

    Each entry: ``{n, status, reason, claim}`` where status ∈
    {"supported", "partial", "unsupported"}. The list is empty when no
    inline citations were found, no references exist, or small_llm is None.

    Failures degrade gracefully — any exception returns an empty list so the
    answer is still served without a verifier badge.
    """
    if not small_llm or not references_all or not answer:
        return []

    pairs = _extract_pairs(answer, max_ref=len(references_all))
    if not pairs:
        return []

    # Cap to avoid runaway prompt size on long answers with many citations.
    pairs = pairs[:24]

    # Build a compact JSON-mode prompt. Each item gets a stable index so the
    # response can map back even if the model reorders.
    items_lines = []
    for idx, pair in enumerate(pairs):
        ref = references_all[pair["ref_n"] - 1]
        items_lines.append(
            f'{{"id": {idx}, "ref_n": {pair["ref_n"]}, '
            f'"claim": {json.dumps(pair["claim"], ensure_ascii=False)}, '
            f'"abstract": {json.dumps(_ref_excerpt(ref), ensure_ascii=False)}}}'
        )
    items_block = "[\n  " + ",\n  ".join(items_lines) + "\n]"

    prompt = f"""You are a citation faithfulness checker for biomedical answers.

For each (claim, abstract) pair below, decide whether the abstract supports
the claim. Use these labels:
- "supported": the abstract states or directly implies the claim.
- "partial": the abstract is topically relevant and partially supports it,
   but is missing key specifics OR adds caveats the claim ignores.
- "unsupported": the abstract does not back up the claim (off-topic or
   contradictory).

Be lenient on phrasing — paraphrase is fine. Be strict on factual content
(numbers, mechanisms, populations).

Items:
{items_block}

Respond with ONLY a JSON array. Each entry: {{"id": <int>, "status":
"supported"|"partial"|"unsupported", "reason": "<≤20 words>"}}. No prose,
no code fences."""

    try:
        resp = small_llm.invoke([HumanMessage(content=prompt)])
        raw = resp.content.strip() if hasattr(resp, "content") else str(resp).strip()
    except Exception:
        logger.warning("Citation verifier LLM call failed", exc_info=True)
        return []

    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", raw, flags=re.DOTALL)
        if not match:
            return []
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return []

    if not isinstance(parsed, list):
        return []

    results: List[Dict[str, Any]] = []
    valid_status = {"supported", "partial", "unsupported"}
    for entry in parsed:
        if not isinstance(entry, dict):
            continue
        try:
            idx = int(entry.get("id"))
        except (TypeError, ValueError):
            continue
        if idx < 0 or idx >= len(pairs):
            continue
        status = str(entry.get("status") or "").strip().lower()
        if status not in valid_status:
            continue
        reason = str(entry.get("reason") or "").strip()[:200]
        pair = pairs[idx]
        results.append({
            "n": pair["ref_n"],
            "status": status,
            "reason": reason,
            "claim": pair["claim"],
        })
    return results
