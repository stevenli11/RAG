# Skill Index

This project uses dual-form skills:
- Documentation skills (`*.SKILL.md`) for governance and policy
- Executable skills (`*.py`) for runtime orchestration

## Executable runtime skills
- `query_router.py`
- `pubmed_evidence.py`
- `protocol_retrieval.py`
- `evidence_grading.py`
- `claim_checker.py`
- `output_template.py`
- `table_formatter.py`
- `reasoning_scaffold.py`
- `wetlab_guardrail.py`
- `evidence_fusion.py`

## Skill docs currently kept
- `query_router.SKILL.md`
- `pubmed_evidence.SKILL.md`
- `protocol_retrieval.SKILL.md`
- `protocol_decision_tree.SKILL.md`
- `evidence_grading.SKILL.md`
- `claim_checker.SKILL.md`
- `output_template.SKILL.md`
- `table_formatter.SKILL.md`
- `reasoning_scaffold.SKILL.md`
- `wetlab_guardrail.SKILL.md`
- `evidence_fusion.SKILL.md`

## Runtime entry
- Orchestrator: `rag_app/runner/orchestrator.py`

## Next implementation step
Add post-generation verification and retry loop (claim-level evidence check + targeted regeneration).
