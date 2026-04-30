"""Route user query to a protocol branch."""

from __future__ import annotations

from typing import Any, Dict

from .base import SkillContext


class QueryRouterSkill:
    name = "query_router"

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        question = str(kwargs.get("question") or "").lower()
        comparison_markers = [
            "compare", "comparison", " versus ", " vs ", "difference between",
            "better than", "pros and cons",
        ]
        protocol_markers = [
            "dose", "dosing", "concentration", "incubation", "protocol", "pipeline",
            "workflow", "step", "assay", "how to run", "parameter", "kit",
            "ph", "p h", "composition", "buffer", "temperature", "duration",
            "timepoint", "timing",
        ]
        knowledge_markers = [
            "what is", "define", "overview", "mechanism", "pathway", "why", "influence",
            "guideline", "evidence", "compare", "versus", "difference",
        ]

        p_hits = sum(1 for k in protocol_markers if k in question)
        k_hits = sum(1 for k in knowledge_markers if k in question)
        c_hits = sum(1 for k in comparison_markers if k in question)

        if c_hits >= 1:
            intent = "comparison"
        elif p_hits >= 2 and p_hits > k_hits:
            intent = "protocol"
        elif p_hits >= 1 and k_hits >= 1:
            intent = "hybrid"
        elif k_hits >= 1:
            intent = "knowledge"
        else:
            # Default to hybrid to avoid under-retrieval for ambiguous scientific questions.
            intent = "hybrid"
        return {"intent": intent, "protocol_hits": p_hits, "knowledge_hits": k_hits, "comparison_hits": c_hits}
