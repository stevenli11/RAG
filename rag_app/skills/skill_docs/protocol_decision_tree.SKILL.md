---
name: protocol_decision_tree
description: Map a question to a protocol path with risk flags and required checks using YAML decision rules.
---

# protocol_decision_tree

## When to use
Use after intent routing to select protocol branch and risk checklist.

## Inputs
- `question` (string)

## Outputs
- `route_id`
- `protocol_path`
- `risk_flags` (list)
- `required_checks` (list)

## Configuration
- Rule file: `rag_app/skills/protocol_tree.yaml`

## Implementation
- Python module: `rag_app/skills/protocol_decision_tree.py`
