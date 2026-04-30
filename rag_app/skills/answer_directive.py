"""Unified answer directive skill.

Replaces OutputTemplateSkill, ReasoningScaffoldSkill, ClaimCheckerSkill,
TableFormatterSkill, and WetlabGuardrailSkill with a single concise
instruction block (<=200 tokens) that guides the LLM without drowning out
the retrieved evidence.
"""

from __future__ import annotations

from typing import Any, Dict

from .base import SkillContext

# Wet-lab detection markers (kept lightweight — the intent from the query
# router is the primary signal; these handle edge cases where intent is
# generic but the question is clearly procedural/lab-oriented).
_WETLAB_MARKERS = frozenset(
    [
        "protocol",
        "assay",
        "experiment",
        "cell line",
        "culture",
        "incubation",
        "concentration",
        "centrifuge",
        "wet lab",
        "pcr",
        "western blot",
        "flow cytometry",
        "staining",
        "transfection",
        "transduction",
        "crispr",
        "knockout",
    ]
)

_HIGH_RISK_MARKERS = frozenset(
    [
        "pathogen",
        "virus",
        "bacteria",
        "biosafety",
        "human subject",
        "patient treatment",
        "clinical intervention",
    ]
)


class AnswerDirectiveSkill:
    """Emit a single short directive paragraph that tells the answer LLM
    *how* to organise and qualify its response for a given question."""

    name = "answer_directive"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_wetlab(question_lower: str, intent: str) -> bool:
        if intent == "protocol":
            return True
        return any(m in question_lower for m in _WETLAB_MARKERS)

    @staticmethod
    def _is_high_risk(question_lower: str) -> bool:
        return any(m in question_lower for m in _HIGH_RISK_MARKERS)

    @staticmethod
    def _wants_table(question_lower: str, intent: str) -> bool:
        compare_markers = ("compare", "comparison", "versus", " vs ", "difference")
        if any(m in question_lower for m in compare_markers):
            return True
        strat_markers = ("stratif", "threshold", "cutoff", "1-49", ">=", "≤")
        if any(m in question_lower for m in strat_markers):
            return True
        return False

    @staticmethod
    def _asks_for_explicit_parameters(question_lower: str) -> bool:
        param_markers = (
            "ph",
            "buffer",
            "composition",
            "concentration",
            "mm",
            "sds",
            "temperature",
            "incubation",
            "time",
            "duration",
            "min",
            "°c",
        )
        return any(m in question_lower for m in param_markers)

    # ------------------------------------------------------------------
    # Directive builders by intent
    # ------------------------------------------------------------------

    def _directive_for_intent(
        self,
        intent: str,
        q: str,
        wants_table: bool,
    ) -> str:
        """Return the core content-organisation hint."""

        if intent == "protocol":
            return (
                "Present as numbered steps with critical parameters "
                "(temperature, concentration, timing). Include controls, "
                "readouts, and failure-point checks."
            )

        if intent == "troubleshoot":
            return (
                "Organise around the natural diagnostic branches. "
                "Start with the most likely cause and work outward."
            )

        if intent == "comparison":
            return (
                "Organise by the axes of comparison found in the evidence. "
                "Use a concise markdown table if it improves readability."
            )

        if intent == "mechanism":
            return (
                "Explain the mechanism step by step. Use a diagram-style "
                "description if the pathway has branches."
            )

        if intent == "stratification":
            return (
                "Organise by the natural clinical strata found in the "
                "evidence. Use a comparison table for agents or regimens. "
                "End with a decision framework."
            )

        if intent == "hybrid":
            return (
                "Balance scientific rationale with actionable "
                "recommendations. Lead with the practical takeaway."
            )

        # intent == "knowledge" or anything else → adaptive
        if wants_table:
            return (
                "Organise by major themes from the evidence. "
                "Include a comparison table where it aids clarity."
            )
        return (
            "Organise by major themes from the evidence. "
            "Highlight consensus vs. controversy."
        )

    # ------------------------------------------------------------------
    # Evidence-quality qualifiers
    # ------------------------------------------------------------------

    # Intents that typically pull from internal SOPs / skill files. For
    # these we always enforce the "quote parameters / don't invent"
    # guardrails and the citation-discipline clause, regardless of
    # whether the question text happens to trigger the wet-lab marker
    # list. See git history for the Turn 3 regression this fixes.
    _PROTOCOL_BACKED_INTENTS = frozenset(
        {"protocol", "troubleshoot", "hybrid", "comparison", "stratification"}
    )

    # Shared across all evidence-quality branches once PubMed is present.
    # Guards against the "citation stuffing" failure mode where the model
    # attaches PubMed refs to mechanistic claims that the abstracts do
    # not actually discuss.
    _CITATION_DISCIPLINE = (
        " Cite a PubMed reference only when the abstract directly supports "
        "the specific claim; do not attach PubMed citations to mechanistic "
        "assertions that the abstract does not explicitly discuss."
    )

    # Appended for protocol-backed intents. Procedural parameters still
    # prefer [internal protocol] markers, but PubMed citations are REQUIRED
    # for scientific rationale, risk discussion, and mechanistic claims
    # surrounding those procedural choices. Earlier wording ("rather than
    # PubMed") drove the LLM to suppress PubMed entirely even when 10+
    # relevant abstracts were retrieved — see the 0/12 regression.
    _INTERNAL_CITATION_PREFERENCE = (
        " Procedural parameters from internal protocols (pH, concentration, "
        "temperature, duration, buffer composition) should be quoted directly "
        "into the prose WITHOUT any provenance marker — do not write "
        "[internal protocol] or similar tags. Use plain numeric citations [N] "
        "for PubMed-supported scientific rationale, risk, and mechanism. If "
        "no abstract supports a specific claim, state it without a citation."
    )

    @classmethod
    def _evidence_qualifier(
        cls,
        has_pubmed: bool,
        quality_counts: Dict[str, int],
        protocol_backed: bool = False,
    ) -> str:
        if not has_pubmed:
            # No PubMed at all — still nudge internal-citation preference
            # when we know the answer is protocol-backed.
            return cls._INTERNAL_CITATION_PREFERENCE if protocol_backed else ""

        high_medium = int(quality_counts.get("high", 0)) + int(
            quality_counts.get("medium", 0)
        )
        low = int(quality_counts.get("low", 0))
        parts: list[str] = []
        # Always require citations when PubMed evidence is present. Evidence
        # grade only affects claim STRENGTH, not citation DENSITY — older
        # logic that skipped citations when only "low" grades existed led to
        # the 0/12 regression on methods-paper questions (grading was biased
        # toward clinical trials, so bench-science refs never got used).
        parts.append(
            " Cite sources inline [1], [2] where claims are directly supported. "
            "Each major section must include at least one inline citation when "
            "PubMed evidence is available."
        )
        if high_medium == 0 and low > 0:
            parts.append(
                " Evidence tier is modest (methods / small-N studies); "
                "temper claims accordingly but still cite the abstracts "
                "inline where they back a specific point."
            )
        parts.append(cls._CITATION_DISCIPLINE)
        if protocol_backed:
            parts.append(cls._INTERNAL_CITATION_PREFERENCE)
            # Hard floor: protocol answers historically dropped PubMed refs
            # entirely (observed 0/12 in the stripping-buffer regression).
            # Applies whenever PubMed is available — even if all refs are
            # graded "low" (methods papers), at least one citation per
            # section anchors the answer in literature.
            parts.append(
                " Citation preference: when a major section makes factual or "
                "scientific claims that a retrieved abstract genuinely supports, "
                "attach a numeric [N] citation. Do not attach citations that the "
                "abstract does not substantively back."
            )
        return "".join(parts)

    # ------------------------------------------------------------------
    # Wet-lab safety suffix
    # ------------------------------------------------------------------

    @staticmethod
    def _safety_suffix(is_wetlab: bool, is_high_risk: bool) -> str:
        if not is_wetlab:
            return ""
        parts = [
            " Safety: do not invent parameters — use TBD when evidence is "
            "missing."
        ]
        if is_high_risk:
            parts.append(
                " High-risk context: add a biosafety/compliance caution and "
                "avoid procedural specifics that increase misuse risk."
            )
        return "".join(parts)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        question = str(kwargs.get("question") or "")
        intent = str(kwargs.get("intent") or "knowledge")
        has_pubmed = bool(kwargs.get("has_pubmed"))
        quality_counts: Dict[str, int] = kwargs.get("quality_counts") or {}

        q = question.lower()

        wetlab = self._is_wetlab(q, intent)
        high_risk = self._is_high_risk(q)
        wants_table = self._wants_table(q, intent)
        asks_params = self._asks_for_explicit_parameters(q)
        protocol_backed = intent in self._PROTOCOL_BACKED_INTENTS

        # Assemble the single directive paragraph.
        directive = self._directive_for_intent(intent, q, wants_table)
        # Comparison nudge: when the question has compare/versus markers the
        # router often still classifies as "hybrid" rather than "comparison"
        # (intents are fuzzy by design). Ensure the table hint survives so the
        # LLM produces a side-by-side even when intent != comparison.
        if wants_table and "comparison table" not in directive.lower() \
                and "concise markdown table" not in directive.lower() \
                and "major themes" not in directive.lower():
            directive += (
                " If the evidence supports it, organise by major themes and "
                "include a concise markdown comparison table."
            )
        # Quote-parameters guardrail fires whenever we have protocol-backed
        # intent (even if the question text doesn't trip wet-lab markers —
        # e.g. "my phospho-signal disappeared after stripping..." which is
        # clearly wet-lab but doesn't contain any of _WETLAB_MARKERS).
        if protocol_backed or (wetlab and asks_params):
            directive += (
                " When internal protocol evidence contains explicit numeric parameters "
                "(pH, concentration, temperature, duration, composition), quote those "
                "values directly in the prose — no provenance tag. Do not claim parameters "
                "are unavailable unless both internal protocol evidence and PubMed evidence lack them."
            )
        if protocol_backed:
            directive += (
                " Ensure each actionable section includes critical parameters "
                "(temperature, concentration, timing) when available."
            )
        directive += self._evidence_qualifier(
            has_pubmed, quality_counts, protocol_backed=protocol_backed
        )
        # Safety suffix also applies to all protocol-backed intents so
        # "do not invent parameters — use TBD" is never dropped for
        # troubleshoot / hybrid queries.
        directive += self._safety_suffix(wetlab or protocol_backed, high_risk)

        return {
            "answer_directive": directive,
            "use_table": wants_table,
            "wetlab_mode": wetlab or protocol_backed,
            "high_risk": high_risk,
        }
