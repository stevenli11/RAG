"""Fuse ranked evidence and answer directive into separate generation inputs."""

from __future__ import annotations

from typing import Any, Dict

from .base import SkillContext


class EvidenceFusionSkill:
    name = "evidence_fusion"

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        pubmed_context = str(kwargs.get("pubmed_context") or "")
        graded_pubmed_context = str(kwargs.get("graded_pubmed_context") or "")
        local_context = str(kwargs.get("local_context") or "")
        answer_directive = str(kwargs.get("answer_directive") or "")
        subquestions_raw = kwargs.get("subquestions") or []
        subquestions = [str(s).strip() for s in subquestions_raw if str(s).strip()]

        # ---- Pre-evidence hard cite directive ----------------------------
        # The SYSTEM_PROMPT already says "use [N] cites only", but the LLM
        # routinely ignored that rule because the evidence block is much
        # closer to the generation tokens (recency bias). The fix is to put
        # an unmistakable, ALL-CAPS reminder at the TOP of the evidence the
        # LLM reads — short, can't be misread as commentary, and right
        # before the abstracts that supply the [N] indices.
        cite_directive = (
            "CITATION FORMAT — STRICT:\n"
            "When making any factual or scientific claim that the ranked PubMed evidence below "
            "supports, attach a numeric inline citation in square brackets, e.g. [1], [2], or "
            "[2, 3] for combined support. Numbers MUST be the [N] labels in the 'Ranked PubMed "
            "evidence' block below. Do NOT use any non-numeric bracket tokens (no [B-CC-021], "
            "[DX-001], [internal protocol], etc). Each major answer section should carry at "
            "least one [N] citation when PubMed evidence supports the claim. Citations are "
            "MANDATORY when evidence supports the statement."
        )

        # Only prepend the directive when we actually have PubMed evidence to
        # cite — telling the LLM "cite [N]" with zero PubMed indices would
        # provoke hallucinated cites.
        has_pubmed = bool(graded_pubmed_context or pubmed_context)
        evidence_parts: list[str] = [cite_directive] if has_pubmed else []
        if subquestions:
            # Prepending the decomposed sub-questions forces the answer LLM
            # to address each one explicitly instead of collapsing a compound
            # question into a single generic response.
            sq_block = "Detected sub-questions (answer EACH with its own sub-section):\n" + "\n".join(
                f"- {s}" for s in subquestions
            )
            evidence_parts.append(sq_block)
        if graded_pubmed_context:
            evidence_parts.append("Ranked PubMed evidence:\n" + graded_pubmed_context)
        elif pubmed_context:
            evidence_parts.append("PubMed studies:\n" + pubmed_context)
        if local_context:
            evidence_parts.append("Internal protocols (retrieval):\n" + local_context)
        evidence = "\n\n".join(evidence_parts)

        # INSTRUCTIONS: the answer directive from AnswerDirectiveSkill
        instructions = answer_directive

        return {
            "evidence": evidence,
            "instructions": instructions,
            # Backward compatibility: app.py currently reads state["context"]
            "context": evidence,
            "has_context": bool(evidence.strip()),
        }
