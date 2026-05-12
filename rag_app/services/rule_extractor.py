"""Parse protocol skill files and extract diagnostic / risk rule entries.

The system uses three skill-file formats with three different rule-ID
conventions:

  - ``western_blot.risk_registry.md``     : markdown table with IDs like
                                             ``B-CC-021`` / ``B-TF-001`` /
                                             ``A-MA-001`` (one letter, dash,
                                             two letters, dash, 3 digits).

  - ``Seahorse...skill.md``               : section headers like
                                             ``### DX-001 LOW_BASELINE_OCR``
                                             followed by Trigger / Likely
                                             cause / Distinguish / Immediate
                                             actions / Prevention paragraphs.

  - ``CRISPR-Cas9.skill.md``              : section headers like
                                             ``### RULE DX-001`` followed by
                                             STAGE / CONDITION / DIAGNOSIS /
                                             LIKELY_CAUSES / DISTINGUISH /
                                             IMMEDIATE_FIX / PREVENTION.

This module reads every skill file once at startup and produces a unified
registry ``{rule_id: {"description", "source_file", "section_title",
"full_text"}}``. Downstream uses:

  - format_service: when sanitising the LLM answer, keep bracketed tokens
    matching IDs in this registry (they are LEGITIMATE references) and
    strip everything else.

  - frontend: hover tooltip shows ``description`` (a 1-2 sentence summary)
    or ``full_text`` (the entire rule body) for the matched rule.

The extractor is intentionally tolerant — if a skill file deviates slightly
from the expected format we still capture the ID and best-effort
description rather than failing.
"""

from __future__ import annotations

import functools
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# Combined ID pattern: matches any of the three known formats.
# Used both for extraction (this module) and for frontend regex (mirrored
# in the React rule-popover component).
_RULE_ID_PATTERN = re.compile(
    r"\b(?:"
    r"(?:RULE\s+)?DX-\d{3}"              # DX-001  /  RULE DX-001
    r"|[A-Z]-[A-Z]{2}-\d{3}"              # B-CC-021 / A-MA-001 etc.
    r")\b"
)

# Pattern for the WB risk_registry table row. Captures ID + last cell
# (the description). The actual table has 6 columns; we want col 1 and
# col 6.
_WB_TABLE_ROW = re.compile(
    r"^\|\s*([A-Z]-[A-Z]{2}-\d{3})\s*"   # ID
    r"\|\s*([^|]+?)\s*"                   # Layer
    r"\|\s*([^|]+?)\s*"                   # Category
    r"\|\s*([^|]+?)\s*"                   # Stage
    r"\|\s*([^|]+?)\s*"                   # Step
    r"\|\s*([^|]+?)\s*\|\s*$",            # Description (final column)
    re.MULTILINE,
)


def _normalize_rule_id(raw: str) -> str:
    """Canonicalise a rule ID so registry lookup is consistent.

    Strip surrounding whitespace, uppercase letters, collapse "RULE DX-001"
    and "DX-001" to the same canonical form when from the same file (we
    keep "RULE " prefix only when present in the section header — but for
    matching purposes we treat them as equivalent).
    """
    return raw.strip().upper()


def _extract_wb_risk_registry(text: str, source_file: str) -> Dict[str, Dict[str, Any]]:
    """Pull every ``| ID | ... | description |`` row out of the WB registry."""
    out: Dict[str, Dict[str, Any]] = {}
    for m in _WB_TABLE_ROW.finditer(text):
        rule_id = _normalize_rule_id(m.group(1))
        layer = m.group(2).strip()
        category = m.group(3).strip()
        stage = m.group(4).strip()
        step = m.group(5).strip()
        description = m.group(6).strip()
        # Some descriptions repeat across IDs (boilerplate parameter risks).
        # We deduplicate on (description) for the same ID — first wins.
        if rule_id in out:
            continue
        out[rule_id] = {
            "id": rule_id,
            "description": description,
            "source_file": source_file,
            "section_title": f"{category} — {stage} {step}",
            "full_text": (
                f"**Layer:** {layer}\n"
                f"**Category:** {category}\n"
                f"**Stage:** {stage}\n"
                f"**Step:** {step}\n\n"
                f"{description}"
            ),
        }
    return out


def _extract_seahorse_dx_rules(text: str, source_file: str) -> Dict[str, Dict[str, Any]]:
    """Pull each ``### DX-NNN NAME`` section out of the Seahorse skill file."""
    out: Dict[str, Dict[str, Any]] = {}
    # Match the header line + everything until the NEXT ``### `` header or
    # ``## `` section break.
    pattern = re.compile(
        r"^###\s+(DX-\d{3})(?:\s+([A-Z_][A-Z_0-9]*))?\s*\n(.*?)(?=^###\s|^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in pattern.finditer(text):
        rule_id = _normalize_rule_id(m.group(1))
        name = (m.group(2) or "").strip()
        body = m.group(3).strip()
        # Description = first non-empty line that follows the "Trigger:"
        # label, or fall back to the first paragraph of the body.
        trigger_match = re.search(r"\*\*Trigger:\*\*\s*(.+?)(?=\*\*|$)", body, re.DOTALL)
        description = (
            trigger_match.group(1).strip() if trigger_match else body.split("\n\n", 1)[0].strip()
        )
        # Trim description to ~280 chars for tooltip readability.
        if len(description) > 280:
            description = description[:277].rstrip() + "..."
        out[rule_id] = {
            "id": rule_id,
            "description": description,
            "source_file": source_file,
            "section_title": name or rule_id,
            "full_text": body,
        }
    return out


def _extract_crispr_rules(text: str, source_file: str) -> Dict[str, Dict[str, Any]]:
    """Pull each ``### RULE DX-NNN`` section out of the CRISPR-Cas9 skill.

    Same rule_id keys as Seahorse (DX-001 etc.) — registry keeps both but
    namespaced by source_file. When the LLM writes ``[RULE DX-001]`` or
    ``[DX-001]`` and the surrounding context is CRISPR, the frontend can
    disambiguate by checking which source_file is relevant.
    """
    out: Dict[str, Dict[str, Any]] = {}
    pattern = re.compile(
        r"^###\s+(?:RULE\s+)?(DX-\d{3})\s*\n(.*?)(?=^###\s|^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in pattern.finditer(text):
        rule_id = _normalize_rule_id(m.group(1))
        body = m.group(2).strip()
        # Description: prefer "DIAGNOSIS:" line, fall back to "CONDITION:".
        diag_match = re.search(r"^DIAGNOSIS:\s*(.+?)$", body, re.MULTILINE)
        cond_match = re.search(r"^CONDITION:\s*(.+?)$", body, re.MULTILINE)
        if diag_match:
            description = diag_match.group(1).strip()
        elif cond_match:
            description = cond_match.group(1).strip()
        else:
            description = body.split("\n", 1)[0].strip()
        if len(description) > 280:
            description = description[:277].rstrip() + "..."
        # Namespace CRISPR rule IDs with a prefix so they don't collide
        # with Seahorse DX-001 etc. in a flat registry. Frontend will
        # accept both ``[DX-001]`` (canonical Seahorse) and
        # ``[RULE DX-001]`` (canonical CRISPR) — see ``_resolve_lookup_keys``.
        key = f"CRISPR/{rule_id}"
        out[key] = {
            "id": rule_id,
            "description": description,
            "source_file": source_file,
            "section_title": f"RULE {rule_id}",
            "full_text": body,
        }
    return out


def _resolve_lookup_keys(rule_id: str, source_hint: Optional[str] = None) -> List[str]:
    """Return registry keys to try for a given raw rule ID.

    ``rule_id`` may arrive in any of these forms from the LLM / sanitizer:
      - ``DX-001``     → try ``DX-001`` (Seahorse) and ``CRISPR/DX-001``
      - ``RULE DX-001`` → try ``CRISPR/DX-001`` first
      - ``B-CC-021``   → try ``B-CC-021`` (WB)

    The optional ``source_hint`` (e.g. "CRISPR-Cas9.skill.md") biases the
    order so the frontend can pass the active skill file as context.
    """
    rid = _normalize_rule_id(rule_id)
    if rid.startswith("RULE "):
        bare = rid.replace("RULE ", "", 1)
        return [f"CRISPR/{bare}"]
    if rid.startswith("DX-"):
        # Ambiguous — try both, biased by source.
        if source_hint and "crispr" in source_hint.lower():
            return [f"CRISPR/{rid}", rid]
        return [rid, f"CRISPR/{rid}"]
    return [rid]


@functools.lru_cache(maxsize=1)
def _protocols_dir() -> Path:
    """Resolve the protocols/ dir the same way ProtocolRetrievalSkill does."""
    project_root = Path(__file__).resolve().parents[2]
    versioned = project_root / "protocols" / "latest"
    flat = project_root / "protocols"
    return versioned if versioned.exists() else flat


# EXACT filenames we know how to parse. Other skill files in protocols/
# are not actively optimised and their internal rule-ID conventions are
# unknown — silently skip them rather than risk wrong parser → collision.
_PARSER_DISPATCH = {
    "western_blot.risk_registry.md": _extract_wb_risk_registry,
    "Seahorse Real-Time Cell Metabolic Analysis.skill.md": _extract_seahorse_dx_rules,
    "CRISPR-Cas9.skill.md": _extract_crispr_rules,
}


@functools.lru_cache(maxsize=1)
def get_rule_registry() -> Dict[str, Dict[str, Any]]:
    """Return the merged rule registry across all known skill files (cached).

    Re-call ``get_rule_registry.cache_clear()`` to force a re-scan after
    editing skill files at runtime.

    Only the 3 actively-optimised skill files contribute rules; other
    files are skipped because their rule-ID conventions (if any) are
    not yet catalogued and we'd risk collisions / wrong descriptions.
    """
    registry: Dict[str, Dict[str, Any]] = {}
    protocols_dir = _protocols_dir()
    if not protocols_dir.exists():
        return registry

    for filename, parser in _PARSER_DISPATCH.items():
        path = protocols_dir / filename
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            logger.warning("Could not read skill file: %s", path, exc_info=True)
            continue
        registry.update(parser(text, filename))

    logger.info("Rule registry built: %d entries", len(registry))
    return registry


def find_rule_references(text: str) -> List[str]:
    """Return every rule-ID-shaped token that appears in ``text``.

    Both bare (``DX-001``) and bracketed (``[DX-001]``) forms are matched.
    Returns the de-duplicated list in first-seen order.
    """
    if not text:
        return []
    seen: List[str] = []
    seen_set: set[str] = set()
    for m in _RULE_ID_PATTERN.finditer(text):
        token = _normalize_rule_id(m.group(0))
        if token not in seen_set:
            seen.append(token)
            seen_set.add(token)
    return seen


def lookup_rule(
    rule_id: str, source_hint: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Return registry entry for a rule ID, or ``None`` if not found."""
    registry = get_rule_registry()
    for key in _resolve_lookup_keys(rule_id, source_hint=source_hint):
        if key in registry:
            return registry[key]
    return None


def build_rule_refs_for_answer(
    answer_text: str,
    protocol_skill_files: List[str] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Scan an answer for rule IDs and return a ``{id: entry}`` map.

    The frontend uses this map to render hover tooltips: it parses the
    same patterns in the answer text and looks each one up.
    """
    refs: Dict[str, Dict[str, Any]] = {}
    if not answer_text:
        return refs
    source_hint = ", ".join(protocol_skill_files or []) if protocol_skill_files else None
    for token in find_rule_references(answer_text):
        entry = lookup_rule(token, source_hint=source_hint)
        if entry:
            # Key the result by the EXACT token the LLM wrote — frontend
            # uses that key directly for the popover lookup.
            refs[token] = entry
    return refs
