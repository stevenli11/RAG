"""Table formatter skill with four fixed table types."""

from __future__ import annotations

from typing import Any, Dict, List

from .base import SkillContext


class TableFormatterSkill:
    name = "table_formatter"

    _TRIGGERS = (
        "compare",
        "comparison",
        "versus",
        "vs",
        "difference",
        "influence",
        "strat",
        "threshold",
        "cutoff",
        "1-49",
        ">=",
        "≤",
        "pd-l1",
    )

    def _should_use_table(self, question: str, intent: str) -> bool:
        q = question.lower()
        # Use table mode only for explicitly comparative / stratified questions.
        compare_markers = ("compare", "comparison", "versus", "vs", "difference")
        if any(m in q for m in compare_markers):
            return True
        if "pd-l1" in q and any(m in q for m in ("1-49", ">=", "≤", "threshold", "cutoff", "strat")):
            return True
        return False

    def _table_type(self, question: str, intent: str) -> str:
        q = question.lower()
        if any(k in q for k in ["pd-l1", "biomarker", "first-line", "patient selection", "guideline", "stage iv"]):
            return "clinical_decision"
        if intent == "protocol" or any(k in q for k in ["protocol", "assay", "step", "workflow", "incubation", "concentration"]):
            return "protocol_execution"
        if any(k in q for k in ["risk", "failure", "artifact", "quality control", "qc", "pitfall", "batch effect"]):
            return "risk_qc"
        return "evidence_comparison"

    def _table_columns(self, table_type: str) -> List[str]:
        if table_type == "clinical_decision":
            return [
                "PD-L1 TPS Group",
                "Recommended Option",
                "Key Evidence",
                "Practical Decision",
                "Reference",
            ]
        if table_type == "protocol_execution":
            return [
                "Step / Decision Point",
                "Parameter / Option",
                "Control & Readout",
                "Risk / Failure Mode",
                "Reference",
            ]
        if table_type == "risk_qc":
            return [
                "Risk / QC Item",
                "Early Signal",
                "Likely Cause",
                "Mitigation Action",
                "Reference",
            ]
        # evidence_comparison (default)
        return [
            "Evidence / Option",
            "Design / Population",
            "Main Finding",
            "Strength / Limitation",
            "Reference",
        ]

    def _type_label(self, table_type: str) -> str:
        mapping = {
            "clinical_decision": "Clinical Decision Table",
            "protocol_execution": "Protocol Execution Table",
            "evidence_comparison": "Evidence Comparison Table",
            "risk_qc": "Risk & QC Table",
        }
        return mapping.get(table_type, "Evidence Comparison Table")

    def _table_instruction(self, table_type: str) -> str:
        base = (
            "Include one concise markdown table after the direct answer. "
            "Keep 3-6 rows, and cite references in the last column with inline ids like [1], [2]."
        )
        if table_type == "clinical_decision":
            return (
                base
                + " Use the minimal PD-L1 TPS strata with exactly 3 core rows: "
                + ">=50%, 1-49%, <1%. "
                + "Do not add extra rows (e.g., squamous-only, PD-L1-unselected, special cohorts) "
                + "unless the user explicitly asks for subgroup expansion. "
                + "Use '<1%' instead of '0%' as the default low-expression category label."
            )
        if table_type == "protocol_execution":
            return base + " Prioritize executability (controls/readouts) over long prose."
        if table_type == "risk_qc":
            return base + " Focus on failure prevention and quality checkpoints."
        return base + " Focus on direct cross-study or cross-option comparison."

    @staticmethod
    def _markdown_header(cols: List[str]) -> str:
        header = "| " + " | ".join(cols) + " |"
        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
        return f"{header}\n{sep}"

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        question = str(kwargs.get("question") or "")
        intent = str(kwargs.get("intent") or "knowledge")

        use_table = self._should_use_table(question=question, intent=intent)
        if not use_table:
            return {
                "use_table": False,
                "table_type": "",
                "table_label": "",
                "table_instruction": "",
                "table_header": "",
            }

        table_type = self._table_type(question=question, intent=intent)
        cols = self._table_columns(table_type)
        header = self._markdown_header(cols)
        instruction = self._table_instruction(table_type)
        table_label = self._type_label(table_type)

        return {
            "use_table": True,
            "table_type": table_type,
            "table_label": table_label,
            "table_instruction": instruction,
            "table_header": header,
        }
