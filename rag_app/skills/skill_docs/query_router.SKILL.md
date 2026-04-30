---
name: query_router
description: Route a user question into a high-level intent class for downstream orchestration.
---

# query_router

## When to use
Use this skill at the start of each chat turn to classify intent.

## Trigger hints
- Mechanism/explanation questions -> `hybrid` or `knowledge`
- Parameter/protocol planning questions -> `protocol`

## Inputs
- `question` (string)

## Outputs
- `intent`: one of `knowledge`, `protocol`, `hybrid`

## Implementation
- Python module: `rag_app/skills/query_router.py`
