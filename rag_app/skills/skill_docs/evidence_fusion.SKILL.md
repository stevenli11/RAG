---
name: evidence_fusion
description: Fuse decision-tree outputs, PubMed evidence, and Milvus protocol evidence into unified context.
---

# evidence_fusion

## When to use
Use before answer generation to produce one coherent context payload.

## Inputs
- `decision` (dict)
- `pubmed_context` (string)
- `local_context` (string)

## Outputs
- `context`
- `has_context` (bool)

## Implementation
- Python module: `rag_app/skills/evidence_fusion.py`
