---
name: protocol_retrieval
description: Retrieve internal protocol text chunks from Milvus and build compact local context.
---

# protocol_retrieval

## When to use
Use when internal protocol knowledge should supplement literature evidence.

## Inputs
- `vectorstore`
- `query` (string)
- `k` (int)
- `max_context_chars` (int)

## Outputs
- `docs`
- `local_context`

## Implementation
- Python module: `rag_app/skills/protocol_retrieval.py`
