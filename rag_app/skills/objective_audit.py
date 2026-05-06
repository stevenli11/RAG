"""ObjectiveAuditSkill — operationalises the "refuse to flatter the user" rule.

Most RAG systems, when a user attaches their experimental data and asks
"how do I optimise this further?", will obediently propose tweaks on top of
that data — even when the data itself is plausibly a false positive / false
negative caused by a setup issue the user hasn't noticed.

This skill runs an extra small_llm pass that:
  1. Reads the diagnostic-rules / risk-rules sections of the selected
     protocol skill file(s) (e.g. DX-001 LOW_BASELINE_OCR rules in the
     Seahorse skill).
  2. Compares the user's stated parameters / observations against those
     known failure modes.
  3. Emits a structured audit listing user assumptions, invalidating
     factors with a citation back to the skill rule, and the weakest
     link of the user's setup.

The audit is then prepended to the evidence block so the answer LLM is
forced to discuss data validity BEFORE recommending optimisations.

Trigger conditions (kept narrow to bound latency cost):
  - Intent is `troubleshoot` or `hybrid`, AND
  - Either the user attached a document, OR the question contains an
    optimisation-style verb ("optimise", "next step", "improve", "调整",
    "下一步", etc.).

If not triggered the skill returns ``{"applied": False}`` and the rest of
the pipeline behaves as before.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage

from .base import SkillContext

logger = logging.getLogger(__name__)


# Verbs that signal the user is asking for a recommendation / next step,
# not just a definitional / explanatory question. Both English and the
# Chinese phrasings the user actually uses in this codebase.
_OPTIMIZATION_VERBS = (
    "optimi", "next step", "improve", "fix", "tweak", "what should",
    "how should i", "调整", "下一步", "怎么办", "怎么优化", "如何优化",
    "如何改进", "改进", "优化",
)


class ObjectiveAuditSkill:
    name = "objective_audit"

    # Cap the failure-mode excerpt fed to small_llm. ~6k chars is enough
    # for one method's full diagnostic rules section (Seahorse DX-001..014
    # is ~5500 chars). Two methods may be selected for compound queries —
    # we still cap globally to avoid blowing up the prompt.
    _SKILL_EXCERPT_BUDGET = 8000

    # Audit fires for these intents; pure-knowledge questions about
    # mechanism / definition do NOT need a validity check. ``protocol``
    # is included because users routinely ask "should I do X first?"
    # questions that are intent-classified as protocol but legitimately
    # need the audit (e.g. "my data has 11 mM glucose in prep medium,
    # should I rerun first or change density?" was being missed).
    _AUDIT_INTENTS = {"troubleshoot", "hybrid", "protocol"}

    # ------------------------------------------------------------------
    # Trigger detection
    # ------------------------------------------------------------------

    @staticmethod
    def _has_optimization_intent(question: str) -> bool:
        q = (question or "").lower()
        return any(v in q for v in _OPTIMIZATION_VERBS)

    @staticmethod
    def _resolve_skill_paths(
        protocol_skill_files: List[str], protocols_dir: Path
    ) -> List[Path]:
        out: List[Path] = []
        for name in protocol_skill_files:
            p = protocols_dir / name
            if p.exists():
                out.append(p)
        return out

    # ------------------------------------------------------------------
    # Failure-mode excerpt extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_failure_mode_section(skill_text: str) -> str:
        """Pull DIAGNOSTIC RULES + RISK RULES sections out of a skill.md.

        Falls back to the whole document for risk-registry style files
        (which don't have those headers and are basically all failure
        modes already, e.g. western_blot.risk_registry.md).
        """
        if not skill_text:
            return ""
        # Match ``## N. DIAGNOSTIC RULES`` / ``## N. RISK RULES`` /
        # ``## DIAGNOSTIC RULES`` headers (case-insensitive) up to the
        # next ``## `` header or EOF.
        sections = []
        for header_pat in (
            r"##\s+\d+\.?\s*DIAGNOSTIC\s+RULES",
            r"##\s+\d+\.?\s*RISK\s+RULES",
            r"##\s+\d+\.?\s*FAILURE\s+MODES",
        ):
            m = re.search(
                rf"({header_pat}.*?)(?=^##\s+\d+\.|\Z)",
                skill_text,
                flags=re.IGNORECASE | re.DOTALL | re.MULTILINE,
            )
            if m:
                sections.append(m.group(1).strip())

        if not sections:
            # Risk-registry style file — no structured sections, the
            # whole file IS the failure-mode catalog.
            return skill_text.strip()

        return "\n\n".join(sections)

    def _gather_failure_modes(
        self, ctx: SkillContext, protocol_skill_files: List[str]
    ) -> Dict[str, str]:
        """Return ``{filename: failure_mode_excerpt}`` for each selected skill."""
        # Resolve protocols directory the same way ProtocolRetrievalSkill
        # does so we don't duplicate logic.
        project_root = Path(__file__).resolve().parents[2]
        versioned = project_root / "protocols" / "latest"
        flat = project_root / "protocols"
        protocols_dir = versioned if versioned.exists() else flat

        out: Dict[str, str] = {}
        budget_left = self._SKILL_EXCERPT_BUDGET
        for path in self._resolve_skill_paths(protocol_skill_files, protocols_dir):
            if budget_left <= 0:
                break
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            excerpt = self._extract_failure_mode_section(text)
            # Per-file slice so a long Seahorse + a long CRISPR don't
            # combine to overflow.
            per_file_cap = max(1500, budget_left // max(1, len(protocol_skill_files)))
            excerpt = excerpt[:per_file_cap]
            if excerpt:
                out[path.name] = excerpt
                budget_left -= len(excerpt)
        return out

    # ------------------------------------------------------------------
    # LLM audit call
    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(
        question: str,
        user_doc_condensed: str,
        failure_modes: Dict[str, str],
    ) -> str:
        if user_doc_condensed:
            user_doc_block = (
                "USER'S UPLOADED EXPERIMENTAL CONTEXT (their numbers, observations,\n"
                "named experimental groups — these are what they want optimised):\n"
                f"<user_doc>\n{user_doc_condensed[:3000].strip()}\n</user_doc>\n\n"
            )
        else:
            user_doc_block = (
                "USER did NOT attach a document. Audit the question itself and\n"
                "any parameters mentioned in the question text against the\n"
                "method's known failure modes.\n\n"
            )

        failure_block = "\n\n".join(
            f"### From `{name}`:\n{excerpt}"
            for name, excerpt in failure_modes.items()
        )
        if not failure_block:
            failure_block = "(No failure-mode catalog available for this method.)"

        return f"""You are an EXPERIMENTAL DATA AUDITOR for a biomedical research assistant.

Your job: refuse to optimise on top of unreliable data. Before any
recommendation is made, audit the user's stated setup / parameters /
observations against the method's KNOWN FAILURE MODES below and decide
whether the user's data is itself reliable.

USER'S QUESTION:
{question}

{user_doc_block}METHOD'S KNOWN FAILURE MODES (canonical, from the protocol skill file):

{failure_block}

YOUR TASK — produce a JSON object with these fields:

{{
  "validity_check_first": true | false,
  "user_assumptions": [
    {{
      "assumption": "<a hidden premise the user is making>",
      "may_be_wrong_because": "<the failure-mode rule that says this could be off>"
    }}
  ],
  "invalidating_factors": [
    {{
      "factor": "<specific concrete way the user's reading could be wrong>",
      "evidence_in_user_data": "<the user's own numbers / setup that triggers it>",
      "skill_rule_ref": "<the rule ID from the failure-mode block that this corresponds to — copy the exact ID format used in that block, e.g. DX-001, RULE DX-002, B-CC-021, B-SI-008, etc. Leave blank if no rule cleanly matches.>"
    }}
  ],
  "weakest_link": "<the single most fragile part of the user's setup — one sentence>",
  "risk_level": "high | medium | low",
  "audit_summary": "<≤30 words: what the answer LLM should tell the user about validity BEFORE any optimisation suggestion>"
}}

RULES:
- Set validity_check_first=true ONLY when the user is asking for an
  optimisation / next-step recommendation AND there is at least one
  concrete invalidating_factor. Otherwise false.
- Quote the user's actual numbers in `evidence_in_user_data`. Do NOT
  invent values they didn't state.
- If you cannot find any failure mode that genuinely applies given the
  user's stated parameters, return empty arrays and risk_level="low".
- Never hedge in audit_summary — be direct: "your basal OCR could be
  ceiling-limited at 30k cells/well, validate density first" beats
  "you might want to consider density".
- Only reference rule IDs that ACTUALLY APPEAR verbatim in the failure-mode
  block above. The block above may contain different ID formats — diagnostic
  rules use DX-NNN or RULE DX-NNN, risk registries use B-XX-NNN or A-XX-NNN
  or X-XX-NNN. Use whatever appears. Do NOT fabricate IDs that aren't there.
- If the failure-mode block is in TABLE form (rows like
  ``| B-CC-002 | Layer B | ... | If phospho-protection is weak, ... |``),
  treat each row as a separate rule and use the leftmost ID column when
  filling skill_rule_ref.

Respond with ONLY the JSON object. No prose, no code fences."""

    def _call_llm(
        self, small_llm: Any, prompt: str
    ) -> Dict[str, Any] | None:
        try:
            resp = small_llm.invoke([HumanMessage(content=prompt)])
            raw = resp.content.strip() if hasattr(resp, "content") else str(resp).strip()
        except Exception:
            logger.warning("ObjectiveAuditSkill LLM call failed", exc_info=True)
            return None

        # Strip code fences if the model added them despite instructions.
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

    @staticmethod
    def _normalize_audit(parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Coerce LLM output to a stable shape, dropping malformed entries."""
        def _clean_str_list_of_dicts(items: Any, required_keys: List[str]) -> List[Dict[str, str]]:
            if not isinstance(items, list):
                return []
            out = []
            for it in items:
                if not isinstance(it, dict):
                    continue
                cleaned = {k: str(it.get(k) or "").strip() for k in required_keys}
                # Keep only entries that have non-empty content for the FIRST key
                if cleaned[required_keys[0]]:
                    out.append(cleaned)
            return out

        risk = str(parsed.get("risk_level") or "low").lower().strip()
        if risk not in {"high", "medium", "low"}:
            risk = "low"

        return {
            "applied": True,
            "validity_check_first": bool(parsed.get("validity_check_first", False)),
            "user_assumptions": _clean_str_list_of_dicts(
                parsed.get("user_assumptions"),
                ["assumption", "may_be_wrong_because"],
            )[:5],
            "invalidating_factors": _clean_str_list_of_dicts(
                parsed.get("invalidating_factors"),
                ["factor", "evidence_in_user_data", "skill_rule_ref"],
            )[:5],
            "weakest_link": str(parsed.get("weakest_link") or "").strip()[:300],
            "risk_level": risk,
            "audit_summary": str(parsed.get("audit_summary") or "").strip()[:400],
        }

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        question = str(kwargs.get("question") or "")
        intent = str(kwargs.get("intent") or "")
        protocol_skill_files: List[str] = list(kwargs.get("protocol_skill_files") or [])
        small_llm = kwargs.get("small_llm")

        # User document condensed text — stashed by ChatOrchestrator.route_question
        # when a session is attached. May be empty.
        user_doc_condensed = str(ctx.state.get("_user_doc_condensed") or "")

        skipped: Dict[str, Any] = {"applied": False, "reason": ""}

        # ---- Trigger gating ------------------------------------------
        if intent not in self._AUDIT_INTENTS:
            skipped["reason"] = f"intent={intent} not in audit set"
            return skipped
        if small_llm is None:
            skipped["reason"] = "no small_llm available"
            return skipped
        if not protocol_skill_files:
            skipped["reason"] = "no protocol skill files selected"
            return skipped
        if not user_doc_condensed and not self._has_optimization_intent(question):
            skipped["reason"] = "no user_doc and no optimisation verb in question"
            return skipped

        # ---- Failure-mode catalog ------------------------------------
        failure_modes = self._gather_failure_modes(ctx, protocol_skill_files)
        if not failure_modes:
            skipped["reason"] = "could not load failure-mode excerpts"
            return skipped

        # ---- LLM call ------------------------------------------------
        prompt = self._build_prompt(question, user_doc_condensed, failure_modes)
        parsed = self._call_llm(small_llm, prompt)
        if parsed is None:
            skipped["reason"] = "audit LLM call failed or returned malformed JSON"
            return skipped

        return self._normalize_audit(parsed)
