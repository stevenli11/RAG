---
name: pubmed_evidence
description: Retrieve PubMed evidence with fallback search strategy and structured context output.
---

# pubmed_evidence

## When to use
Use for evidence-backed responses requiring literature support.

## Inputs
- `question` (string)
- `rewritten_question` (string, optional)
- `small_llm` (optional)
- `max_results` (int)

## Outputs
- `query_used`
- `articles`
- `context`
- `references`

## Notes
Search strategy uses fallback order:
1. base question
2. LLM-generated PubMed query
3. simplified keyword query

## Implementation
- Python module: `rag_app/skills/pubmed_evidence.py`
