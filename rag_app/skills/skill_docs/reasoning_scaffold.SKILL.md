---
name: reasoning_scaffold
type: executable-skill
module: rag_app/skills/reasoning_scaffold.py
---

# reasoning_scaffold

Purpose:
- Enforce a global layer-by-layer answer logic for all questions, not case-specific prompt patches.

Layered structure:
1. Direct answer
2. Minimal framework (table/bullets)
3. Decision/action mapping
4. Caveats and uncertainty
5. Action checklist

Outputs:
- `scaffold_enabled`
- `scaffold_name`
- `scaffold_instruction`

