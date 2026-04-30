"""Wet-lab guardrail skill for safer and more executable lab guidance."""

from __future__ import annotations

from typing import Any, Dict, List

from .base import SkillContext


class WetlabGuardrailSkill:
    name = "wetlab_guardrail"

    _WETLAB_MARKERS = (
        "protocol",
        "experiment",
        "assay",
        "sample",
        "cell line",
        "culture",
        "incubation",
        "concentration",
        "dose",
        "temperature",
        "centrifuge",
        "wet lab",
        "pcr",
        "western blot",
        "flow cytometry",
        "staining",
    )
    _HIGH_RISK_MARKERS = (
        "pathogen",
        "virus",
        "bacteria",
        "biosafety",
        "human subject",
        "patient treatment",
        "clinical intervention",
    )

    def _is_wetlab_question(self, question: str, intent: str) -> bool:
        q = question.lower()
        if intent == "protocol":
            return True
        return any(m in q for m in self._WETLAB_MARKERS)

    def _is_high_risk(self, question: str) -> bool:
        q = question.lower()
        return any(m in q for m in self._HIGH_RISK_MARKERS)

    def _build_rules(self, high_risk: bool) -> List[str]:
        rules = [
            "Safety boundary: decline hazardous, regulated, or clinical intervention procedures; provide compliance-safe alternatives.",
            "Parameter truthfulness: do not invent concentration/time/temperature/dose/centrifuge settings. Use TBD if evidence is missing.",
            "Evidence hierarchy: prioritize guideline/meta-analysis > randomized trial > cohort/retrospective > in-vitro/preclinical.",
            "Context lock: identify species, tissue/cell line, disease context, and assay platform before final recommendations.",
            "Executability: include materials/input, key steps, controls, readouts, and failure-point checks.",
            "Citation governance: every key claim should have inline citations when PubMed evidence exists.",
            "Uncertainty style: provide best-effort answer first, then a concise uncertainty note.",
            "Auditability: clearly separate evidence-backed parameters from assumptions/defaults.",
        ]
        if high_risk:
            rules.append("High-risk mode: add an explicit biosafety/compliance caution and avoid procedural specifics that increase misuse risk.")
        return rules

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        question = str(kwargs.get("question") or "")
        intent = str(kwargs.get("intent") or "knowledge")
        wetlab_mode = self._is_wetlab_question(question, intent)
        high_risk = self._is_high_risk(question)

        if not wetlab_mode:
            return {
                "wetlab_mode": False,
                "high_risk": False,
                "guardrail_instruction": "",
                "guardrail_summary": "Wet-lab guardrail not activated for this question.",
            }

        rules = self._build_rules(high_risk=high_risk)
        instruction = "\n".join(f"- {r}" for r in rules)

        summary = "Wet-lab guardrail enabled"
        if high_risk:
            summary += " (high-risk policy active)"

        return {
            "wetlab_mode": True,
            "high_risk": high_risk,
            "guardrail_instruction": instruction,
            "guardrail_summary": summary + ".",
        }

