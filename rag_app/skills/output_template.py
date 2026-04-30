"""Output template skill — short contextual hints that complement the main prompt."""

from __future__ import annotations

from typing import Any, Dict

from .base import SkillContext


class OutputTemplateSkill:
    name = "output_template"

    @staticmethod
    def _detect_mode(question: str, intent: str) -> str:
        """Broad mode tag based on question shape, not domain keywords."""
        q = (question or "").lower()

        if any(k in q for k in [
            "troubleshoot", "troubleshooting", "why failed", "failed",
            "failure", "not working", "low viability", "contamination",
            "no signal", "poor yield",
        ]):
            return "troubleshoot"
        if any(k in q for k in ["compare", "difference", "versus", "vs"]):
            return "comparison"
        if any(k in q for k in [
            "influence", "affect", "impact", "determine", "guide",
            "selection", "stratif", "classify", "categoriz",
        ]):
            return "stratification"
        if any(k in q for k in [
            "protocol", "assay", "workflow", "steps", "how to run",
            "how do i", "how to set up", "procedure",
        ]):
            return "action"
        return "adaptive"

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        question = str(kwargs.get("question") or "")
        intent = str(kwargs.get("intent") or "knowledge")
        has_pubmed = bool(kwargs.get("has_pubmed"))
        quality_counts = kwargs.get("quality_counts") or {}
        high_medium = int(quality_counts.get("high", 0)) + int(
            quality_counts.get("medium", 0)
        )
        low_only_pubmed = has_pubmed and high_medium == 0
        mode = self._detect_mode(question=question, intent=intent)

        # Only add short hints that the main prompt skeleton doesn't cover.
        lines = []

        if mode == "troubleshoot":
            lines.append(
                "Hint: organize around the natural diagnostic branches "
                "and keep the logic easy to scan."
            )
        elif mode == "comparison":
            lines.append(
                "Hint: use a comparison table only if it improves "
                "readability; otherwise keep the comparison compact."
            )
        elif mode == "stratification":
            lines.append(
                "Hint: organize by natural thresholds or subgroups, "
                "but do not force fixed section labels."
            )
        elif mode == "action":
            lines.append(
                "Hint: favor steps, controls, and readouts when the "
                "question is procedural."
            )

        if has_pubmed:
            if low_only_pubmed:
                lines.append(
                    "Evidence is low-only — keep claims modest and avoid "
                    "forcing citations."
                )
            else:
                lines.append(
                    "Use inline citations [1], [2] only where claims are "
                    "directly supported."
                )

        template = "\n".join(lines) if lines else ""
        return {"output_template": template, "template_style": mode}
