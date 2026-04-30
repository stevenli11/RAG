"""Claim checker skill — evidence-related constraints only, no layout rules."""

from __future__ import annotations

from typing import Any, Dict

from .base import SkillContext


class ClaimCheckerSkill:
    name = "claim_checker"

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        question = str(kwargs.get("question") or "")
        has_pubmed = bool(kwargs.get("has_pubmed"))
        quality_counts = kwargs.get("quality_counts") or {}
        high_medium = int(quality_counts.get("high", 0)) + int(quality_counts.get("medium", 0))
        low_only_pubmed = has_pubmed and high_medium == 0

        instructions = [
            "Only make strong claims when there is explicit support in provided evidence.",
            "Keep claims modest when evidence is weak.",
            "Use inline numeric citations [1], [2] only for directly supported claims.",
            "Do not add raw URLs in the body.",
        ]

        if has_pubmed:
            if low_only_pubmed:
                instructions.append(
                    "Low-only PubMed mode: do not force citation density or "
                    "quality-disclaimer paragraphs."
                )

        q = question.lower()
        if any(k in q for k in ["how", "influence", "compare", "versus", "difference"]):
            instructions.append(
                "Use comparative phrasing and explain decision logic."
            )

        contract = "\n".join(f"- {item}" for item in instructions)

        return {
            "answer_contract": contract,
            "min_inline_citations": 0,
            "has_pubmed": has_pubmed,
        }
