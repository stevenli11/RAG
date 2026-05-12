"""Output formatting and sanitization helpers."""

from __future__ import annotations

import re


def sanitize_nonstandard_citation_tags(text: str) -> str:
    """Sanitise stray bracket tokens in the LLM answer.

    Policy:
      - ``[1]`` / ``[2, 3]`` — numeric PubMed citations: ALWAYS keep.
      - ``[B-CC-021]`` / ``[DX-001]`` / ``[RULE DX-003]`` — these are
        legitimate references to internal protocol rules WHEN they map
        to a known entry in the rule registry. KEEP them so the frontend
        can render hover popovers showing the rule description.
      - ``[B-XX-XXX]`` shaped tokens that DON'T resolve to any known rule
        — strip (the LLM made one up).
      - ``[internal protocol]`` / ``[Retrieved ...]`` / ``[source]`` —
        narrative placeholders: strip.

    The previous behaviour was to strip ALL alphanumeric bracket tokens
    indiscriminately, which threw away legitimate rule references the
    user wanted to look up. The shift to a whitelist via the rule
    registry keeps the useful refs and only nukes hallucinated ones.
    """
    if not text:
        return text

    # ``[Retrieved …]`` → ``(Retrieved …)`` (legacy behaviour).
    text = re.sub(r"\[(Retrieved[^\]]+)\]", r"(\1)", text, flags=re.IGNORECASE)
    # Narrative-only placeholders the LLM still occasionally writes.
    text = re.sub(
        r"\[\s*(internal protocol|internal-protocol|source|protocol)\s*\]",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Now the interesting case: alphanumeric IDs. Keep KNOWN rules,
    # strip unknown ones. Import lazily to avoid a circular import at
    # module load (format_service is itself imported by chat_service
    # while rag_app may not be initialised yet in some test paths).
    try:
        from rag_app.services.rule_extractor import lookup_rule
    except Exception:
        lookup_rule = None  # type: ignore[assignment]

    def _process_alpha_bracket(m: re.Match) -> str:
        body = m.group(1)
        raw_tokens = [t.strip() for t in body.split(",") if t.strip()]
        if not raw_tokens:
            return m.group(0)
        # If EVERY token resolves to a known rule, keep the whole bracket.
        if lookup_rule is not None and all(lookup_rule(t) is not None for t in raw_tokens):
            return m.group(0)
        # If NO token is a rule-id-shape, also keep (probably real content).
        if not any(
            re.fullmatch(r"(?:RULE\s+)?[A-Z]+(?:-[A-Z]+)*-?\d+", t) for t in raw_tokens
        ):
            return m.group(0)
        # Mix or all-unknown rule-shaped → likely hallucinated, strip.
        return ""

    # Match brackets whose contents look like rule IDs (uppercase + digits
    # + hyphens + optional comma-separated list + optional 'RULE ' prefix).
    text = re.sub(
        r"\[([A-Z][A-Za-z0-9,\-\s]*?)\]",
        _process_alpha_bracket,
        text,
    )

    # Collapse double-spaces / dangling punctuation left by a removed bracket.
    text = re.sub(r"  +", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text


def soft_wrap_long_lines(text: str, max_len: int = 260) -> str:
    """Insert line breaks for long prose lines while preserving markdown tables/code."""
    if not text:
        return text
    out = []
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if len(line) <= max_len:
            out.append(line)
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            out.append(line)
            continue
        if "|" in stripped and stripped.count("|") >= 3:
            out.append(line)
            continue
        if stripped.startswith("```") or stripped.startswith("    "):
            out.append(line)
            continue
        parts = re.split(r"(?<=[\.\?!;:])\s+", stripped)
        cur = ""
        for p in parts:
            if not p:
                continue
            trial = f"{cur} {p}".strip()
            if len(trial) <= max_len or not cur:
                cur = trial
            else:
                out.append(cur)
                cur = p
        if cur:
            out.append(cur)
    return "\n".join(out)

