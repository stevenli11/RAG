"""Lightweight rubric scoring for wet-lab assistant answers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


DIMENSIONS = [
    "goal_understanding",
    "executability",
    "risk_judgment",
    "parameter_honesty",
    "evidence_quality",
    "citation_integration",
    "uncertainty_handling",
    "decision_quality",
    "reproducibility",
    "clarity",
]

DIMENSION_LABELS = {
    "goal_understanding": "Goal Understanding",
    "executability": "Executability",
    "risk_judgment": "Risk Judgment",
    "parameter_honesty": "Parameter Honesty",
    "evidence_quality": "Evidence Quality",
    "citation_integration": "Citation Integration",
    "uncertainty_handling": "Uncertainty Handling",
    "decision_quality": "Decision Quality",
    "reproducibility": "Reproducibility",
    "clarity": "Clarity",
}


def _clip_1_5(x: float) -> float:
    return max(1.0, min(5.0, round(x, 1)))


def _contains_any(text: str, keywords: List[str]) -> int:
    lower = text.lower()
    return sum(1 for k in keywords if k in lower)


def _extract_inline_citation_count(answer: str) -> int:
    # Match [1], [2], or markdown-linked [1](...)
    return len(re.findall(r"\[(\d+)\](?:\([^)]+\))?", answer))


def _extract_reference_count(answer: str, references: List[str]) -> int:
    if references:
        return len(references)
    if "references" in answer.lower():
        # Rough fallback when references were appended into answer body.
        tail = answer.lower().split("references", 1)[-1]
        return len(re.findall(r"\[\d+\]", tail))
    return 0


def _infer_question_profile(question: str) -> Dict[str, bool]:
    q = (question or "").lower()
    troubleshooting_kw = [
        "troubleshoot", "troubleshooting", "failed", "failure", "low viability",
        "background", "smear", "not working", "improve", "optimize", "qc", "contamination"
    ]
    conceptual_kw = [
        "what is", "difference", "compare", "vs", "versus", "when should",
        "why", "principle", "concept"
    ]
    protocol_kw = [
        "step", "workflow", "process", "actionable", "protocol", "how to", "decision"
    ]
    return {
        "troubleshooting": any(k in q for k in troubleshooting_kw),
        "conceptual": any(k in q for k in conceptual_kw),
        "protocol_or_actionable": any(k in q for k in protocol_kw),
    }


def _top_weak_dimensions(scores: Dict[str, float], n: int = 2) -> List[Tuple[str, float]]:
    ranked = sorted(scores.items(), key=lambda x: x[1])
    return ranked[:n]


@dataclass
class ScoreResult:
    dimension_scores: Dict[str, float]
    overall: float
    notes: List[str]


def score_answer(question: str, answer: str, references: List[str] | None = None) -> ScoreResult:
    refs = references or []
    q = question or ""
    a = answer or ""

    inline_citations = _extract_inline_citation_count(a)
    ref_count = _extract_reference_count(a, refs)
    bullet_count = len(re.findall(r"^\s*[-*]\s+", a, flags=re.MULTILINE))
    numbered_count = len(re.findall(r"^\s*\d+\.\s+", a, flags=re.MULTILINE))
    number_tokens = len(re.findall(r"\b\d+(\.\d+)?\b", a))

    q_keywords = re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", q.lower())
    q_keywords = [w for w in q_keywords if w not in {"what", "how", "why", "with", "from", "this", "that"}]
    overlap = sum(1 for w in set(q_keywords[:12]) if w in a.lower())

    s_goal = _clip_1_5(2.0 + min(3.0, overlap * 0.35))
    s_exec = _clip_1_5(1.8 + _contains_any(a, ["step", "protocol", "control", "readout", "assay", "workflow"]) * 0.6 + min(1.0, (bullet_count + numbered_count) * 0.2))
    s_risk = _clip_1_5(1.8 + _contains_any(a, ["risk", "failure", "artifact", "pitfall", "bias", "safety", "qc"]) * 0.7)

    honesty_bonus = 0.0
    if _contains_any(a, ["tbd", "not provided", "missing", "clarify", "assumption", "uncertain"]) > 0:
        honesty_bonus += 1.2
    if number_tokens > 25 and inline_citations == 0:
        honesty_bonus -= 0.7
    s_honesty = _clip_1_5(2.5 + honesty_bonus)

    evidence_hits = _contains_any(a, ["trial", "randomized", "guideline", "meta-analysis", "systematic review", "cohort"])
    s_evidence = _clip_1_5(1.8 + min(1.5, evidence_hits * 0.35) + min(1.7, ref_count * 0.25))
    s_cite = _clip_1_5(1.4 + min(3.0, inline_citations * 0.35))
    s_uncertainty = _clip_1_5(2.2 + _contains_any(a, ["uncertain", "limited", "depends", "if", "however"]) * 0.4)
    s_decision = _clip_1_5(1.8 + _contains_any(a, ["recommend", "prefer", "choose", "versus", "decision", "therefore"]) * 0.6)
    s_repro = _clip_1_5(1.8 + _contains_any(a, ["replicate", "repeat", "qc", "quality control", "validation", "checkpoint"]) * 0.7)

    length_factor = min(1.2, len(a) / 900.0)
    structure_factor = min(1.2, (bullet_count + numbered_count) * 0.15)
    s_clarity = _clip_1_5(2.2 + length_factor + structure_factor)

    scores = {
        "goal_understanding": s_goal,
        "executability": s_exec,
        "risk_judgment": s_risk,
        "parameter_honesty": s_honesty,
        "evidence_quality": s_evidence,
        "citation_integration": s_cite,
        "uncertainty_handling": s_uncertainty,
        "decision_quality": s_decision,
        "reproducibility": s_repro,
        "clarity": s_clarity,
    }
    overall = _clip_1_5(sum(scores.values()) / len(scores))
    profile = _infer_question_profile(q)

    notes = []
    if inline_citations < 2 and ref_count > 0:
        notes.append("Inline citations are sparse; add more sentence-level citations.")
    if ref_count == 0:
        notes.append("No references detected.")
    if s_exec < 3.0 and profile["protocol_or_actionable"]:
        notes.append("Executability is weak; include controls/readouts and concrete steps.")
    if s_risk < 3.0 and profile["troubleshooting"]:
        notes.append("Risk analysis is weak for a troubleshooting query; add failure modes and QC checks.")

    # If no specific note fired, emit one concise note from the weakest dimension,
    # instead of repeating generic risk/QC language every time.
    if not notes:
        weakest = _top_weak_dimensions(scores, n=1)[0][0]
        if weakest == "citation_integration":
            notes.append("Citation integration can be improved by mapping each key claim to one reference.")
        elif weakest == "decision_quality":
            notes.append("Decision quality can improve with clearer prioritization (what to do first/next).")
        elif weakest == "clarity":
            notes.append("Clarity can improve with shorter sections and stronger heading separation.")

    return ScoreResult(dimension_scores=scores, overall=overall, notes=notes)
