"""Fuse ranked evidence and answer directive into separate generation inputs."""

from __future__ import annotations

from typing import Any, Dict

from .base import SkillContext


class EvidenceFusionSkill:
    name = "evidence_fusion"

    @staticmethod
    def _render_audit_block(audit: Dict[str, Any]) -> str:
        """Format the objective-audit JSON into a directive block.

        Heavily worded on purpose: the answer LLM has demonstrably ignored
        soft "consider whether..." phrasing in past iterations, so this
        block uses imperatives and front-loads the validity-check
        directive when ``validity_check_first`` is set.
        """
        check_first = bool(audit.get("validity_check_first"))
        risk_level = str(audit.get("risk_level") or "low").lower()
        invalidating = list(audit.get("invalidating_factors") or [])
        assumptions = list(audit.get("user_assumptions") or [])
        weakest_link = str(audit.get("weakest_link") or "").strip()
        summary = str(audit.get("audit_summary") or "").strip()

        lines: list[str] = []
        if check_first:
            lines.append(
                "OBJECTIVE DATA AUDIT — VALIDITY CHECK MUST COME FIRST:"
            )
            lines.append(
                "Before recommending any optimisation or next-step tweak, "
                "your answer MUST OPEN with the validity concerns below. "
                "Do NOT proceed to optimisation suggestions on top of data "
                "that may itself be unreliable."
            )
        else:
            lines.append("OBJECTIVE DATA AUDIT:")

        lines.append(f"Risk level: {risk_level}")

        if summary:
            lines.append(f"Summary: {summary}")

        if invalidating:
            lines.append("\nInvalidating factors (the user's data may be wrong because):")
            for f in invalidating:
                factor = str(f.get("factor") or "").strip()
                evidence = str(f.get("evidence_in_user_data") or "").strip()
                rule_ref = str(f.get("skill_rule_ref") or "").strip()
                bullet = f"- {factor}"
                if evidence:
                    bullet += f" — evidence in user data: {evidence}"
                if rule_ref:
                    bullet += f" (cf. {rule_ref})"
                lines.append(bullet)

        if assumptions:
            lines.append("\nHidden user assumptions worth challenging:")
            for a in assumptions:
                assumption = str(a.get("assumption") or "").strip()
                why = str(a.get("may_be_wrong_because") or "").strip()
                bullet = f"- {assumption}"
                if why:
                    bullet += f" — questionable because: {why}"
                lines.append(bullet)

        if weakest_link:
            lines.append(f"\nWeakest link in user's setup: {weakest_link}")

        return "\n".join(lines)

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        pubmed_context = str(kwargs.get("pubmed_context") or "")
        graded_pubmed_context = str(kwargs.get("graded_pubmed_context") or "")
        local_context = str(kwargs.get("local_context") or "")
        answer_directive = str(kwargs.get("answer_directive") or "")
        subquestions_raw = kwargs.get("subquestions") or []
        subquestions = [str(s).strip() for s in subquestions_raw if str(s).strip()]
        audit = kwargs.get("audit") or None  # ObjectiveAuditSkill output, or None

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

        # ---- ObjectiveAudit block (when present) -------------------------
        # Goes ABOVE everything else so the answer LLM addresses the
        # validity-check directive before reading any PubMed evidence or
        # protocol context. This is the load-bearing piece that makes the
        # "refuse to flatter the user" behaviour actually take effect.
        if audit and audit.get("applied"):
            evidence_parts.append(self._render_audit_block(audit))

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
