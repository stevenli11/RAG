---
name: table_formatter
type: executable-skill
module: rag_app/skills/table_formatter.py
---

# table_formatter

Purpose:
- Improve readability for complex answers by injecting a compact markdown table when the question is comparison-like.

Trigger:
- Enabled for comparison/threshold/stratification signals (e.g., compare, versus, threshold, PD-L1 groups).

Behavior:
- Auto-selects one of four fixed table types:
  - `clinical_decision`
  - `protocol_execution`
  - `evidence_comparison`
  - `risk_qc`
- Adds a table instruction plus a recommended markdown header.
- Keeps table optional for non-comparative questions.

Outputs:
- `use_table`
- `table_type`
- `table_label`
- `table_instruction`
- `table_header`
