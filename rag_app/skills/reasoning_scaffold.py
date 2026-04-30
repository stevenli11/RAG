"""Global reasoning scaffold — thinking cues only, no layout duplication."""

from __future__ import annotations

from typing import Any, Dict

from .base import SkillContext


class ReasoningScaffoldSkill:
    name = "reasoning_scaffold"

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        intent = str(kwargs.get("intent") or "knowledge")
        quality_counts = kwargs.get("quality_counts") or {}
        high_medium = int(quality_counts.get("high", 0)) + int(
            quality_counts.get("medium", 0)
        )
        low_only_pubmed = int(quality_counts.get("low", 0)) > 0 and high_medium == 0
        use_table = bool(kwargs.get("use_table"))

        parts = [
            "Before writing, scan the evidence for the natural way to "
            "organize the answer.",
        ]

        if low_only_pubmed:
            parts.append(
                "Evidence is low-only — keep claims modest."
            )

        if intent == "protocol":
            parts.append(
                "Protocol focus: ensure controls, readouts, and failure "
                "checks."
            )
        elif intent == "hybrid":
            parts.append(
                "Balance rationale with actionable recommendations."
            )

        if use_table:
            parts.append(
                "If a table helps, use valid markdown table syntax."
            )

        scaffold = "\n".join(parts)
        return {
            "scaffold_enabled": True,
            "scaffold_name": "adaptive_v3",
            "scaffold_instruction": scaffold,
        }
