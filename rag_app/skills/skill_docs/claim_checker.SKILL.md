---
name: claim_checker
type: executable-skill
module: rag_app/skills/claim_checker.py
---

# claim_checker

Purpose:
- Define pre-generation guardrails so answers remain direct, evidence-linked, and non-refusal in tone.

Current behavior:
- Enforces "answer first" style.
- Sets minimum inline citation count when PubMed evidence exists.
- Requests short uncertainty note only when evidence is weak.

Inputs:
- `question`
- `has_pubmed`
- `quality_counts`

Outputs:
- `answer_contract`
- `min_inline_citations`
- `has_pubmed`

