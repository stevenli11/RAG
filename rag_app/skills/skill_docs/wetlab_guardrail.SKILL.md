---
name: wetlab_guardrail
type: executable-skill
module: rag_app/skills/wetlab_guardrail.py
---

# wetlab_guardrail

Purpose:
- Apply wet-lab specific safety, evidence, and executability rules before final generation.

Rules covered:
- Safety boundary and misuse prevention
- Parameter truthfulness (`TBD` when unsupported)
- Evidence hierarchy discipline
- Species/tissue/cell-line context lock
- Executable output requirements (controls/readouts/checkpoints)
- Citation governance
- Uncertainty style (answer first, short caveat)
- Audit-ready separation of evidence vs assumptions

Outputs:
- `wetlab_mode`
- `high_risk`
- `guardrail_instruction`
- `guardrail_summary`

