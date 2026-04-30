"""Turn-level telemetry for QA and regression debugging."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from .citation_service import has_inline_citation_markers


def doc_source_label(doc: Any) -> str:
    """Get a stable short source label from document metadata."""
    meta = getattr(doc, "metadata", {}) or {}
    for key in ("protocol_relpath", "source", "file_path", "path", "skill_id", "title"):
        val = meta.get(key)
        if val:
            return str(val).split("/")[-1]
    return "unknown_source"


def readability_signals(text: str) -> tuple[str, List[str]]:
    """Heuristic readability checker."""
    if not text:
        return "unknown", ["empty answer"]
    lines = text.splitlines()
    non_table = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        if "|" in stripped and stripped.count("|") >= 3:
            continue
        non_table.append(line)
    max_line_len = max((len(line) for line in non_table), default=0)
    reasons = []
    if max_line_len > 320:
        reasons.append(f"very long line ({max_line_len} chars)")
    return ("warn", reasons) if reasons else ("ok", [])


def build_turn_observation(
    *,
    question: str,
    docs: List[Any],
    pubmed_articles: List[Dict[str, Any]],
    answer_text: str,
    display_text: str,
) -> Dict[str, Any]:
    """Build normalized OBS payload."""
    top_sources = []
    for doc in docs[:3]:
        label = doc_source_label(doc)
        if label not in top_sources:
            top_sources.append(label)
    citation_ok = (not pubmed_articles) or has_inline_citation_markers(display_text)
    readability, notes = readability_signals(answer_text)
    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": question,
        "top3_sources": top_sources or ["none"],
        "pubmed_zero_results": not bool(pubmed_articles),
        "citation_clickable": citation_ok,
        "readability": readability,
        "readability_notes": notes,
    }


def print_turn_observation(obs: Dict[str, Any]) -> None:
    """Print OBS summary in existing console style."""
    print("\n[OBS] ---------------- Turn Observation ----------------", flush=True)
    print(f"[OBS] time={obs.get('time')}", flush=True)
    print(f"[OBS] query={obs.get('query')}", flush=True)
    print(f"[OBS] top3_sources={obs.get('top3_sources')}", flush=True)
    print(
        f"[OBS] pubmed_zero_results={'yes' if obs.get('pubmed_zero_results') else 'no'}",
        flush=True,
    )
    print(
        f"[OBS] citation_clickable={'yes' if obs.get('citation_clickable') else 'warn'}",
        flush=True,
    )
    if obs.get("readability_notes"):
        print(
            f"[OBS] readability={obs.get('readability')} ({'; '.join(obs['readability_notes'])})",
            flush=True,
        )
    else:
        print(f"[OBS] readability={obs.get('readability')}", flush=True)
    print("[OBS] ----------------------------------------------------\n", flush=True)

