"""Output formatting and sanitization helpers."""

from __future__ import annotations

import re


def sanitize_nonstandard_citation_tags(text: str) -> str:
    """Replace non-standard bracket tags like [Retrieved ...] / [B-CC-021] with
    plain notes so they don't get mistaken for citations downstream.

    Two failure modes this fixes:
      1. ``[Retrieved protocol context #N]`` style bracketed prose tags — old.
      2. Internal-protocol entry IDs (``[B-CC-021]``, ``[B-DT-022]``,
         ``[DX-001]``, ``[RULE DX-009]``, etc.) that LLMs occasionally
         use as faux citations after seeing them in the evidence block.
         These tokens are alphanumeric+hyphen only — they never collide
         with the legitimate numeric ``[1]`` / ``[1, 3]`` cite format,
         so it's safe to strip them out.

    The cite-extractor downstream (``extract_cited_reference_indices``) only
    matches ``[(\\d+(?:\\s*,\\s*\\d+)*)]``, so these alphanumeric brackets
    don't get counted as cites either way; this sanitizer's job is to keep
    them from polluting the rendered answer text the user sees.
    """
    if not text:
        return text
    text = re.sub(r"\[(Retrieved[^\]]+)\]", r"(\1)", text, flags=re.IGNORECASE)
    # Strip internal-protocol entry IDs: ``[X-NN]`` or ``[X-XX-NNN]``
    # patterns — at least one letter group, separated by hyphens, optionally
    # followed by digits. Lists inside one bracket are also matched
    # (``[B-CC-021, B-DT-022]``).
    def _strip_internal(m: re.Match) -> str:
        body = m.group(1)
        tokens = [t.strip() for t in body.split(",")]
        # Only drop if EVERY comma-separated token looks like an internal ID.
        if tokens and all(re.fullmatch(r"[A-Z]+(?:-[A-Z]+)*-?\d+", t) for t in tokens):
            return ""
        return m.group(0)

    text = re.sub(r"\[([A-Z][A-Za-z0-9,\-\s]*)\]", _strip_internal, text)
    # Collapse any double-spaces left behind by a removed bracket.
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

