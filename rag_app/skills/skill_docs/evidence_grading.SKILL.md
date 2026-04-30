<!--
 * @Author: Peng Li
 * @Date: 2026-03-10 00:52:19
 * @LastEditors: Peng Li
 * @LastEditTime: 2026-04-23 17:15:21
 * @FilePath: /RAG_local/rag_app/skills/skill_docs/evidence_grading.SKILL.md
 * @Description: 
-->
---
name: evidence_grading
description: Grade evidence strength and propagate the grade into answer language.
---

# evidence_grading

## Purpose
Ensure claims are aligned with evidence quality.

## Inputs
- `pubmed_hits`
- `internal_protocol_hits`
- optional: `study_metadata`

## Outputs
- `evidence_grade` (`A`/`B`/`C`/`D`)
- `grade_rationale`
- `allowed_assertion_strength`

## Suggested grading logic
- A: Multiple high-quality, directly relevant studies (trial-level preferred)
- B: Moderate direct evidence
- C: Limited or indirect evidence
- D: Weak evidence or no direct support

## Language policy
- Grade A/B: can use confident recommendation language
- Grade C/D: must use cautious language and uncertainty statement
