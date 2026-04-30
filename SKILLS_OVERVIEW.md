# Skill-driven Pipeline

The chat backend orchestrates retrieval and reasoning as a sequence of small,
swappable skills under `rag_app/skills/`. The orchestrator
(`rag_app/runner/orchestrator.py`) is split into two phases so the streaming
HTTP route can emit early UI events while the slower retrieval continues.

## Phase 1 — routing (fast)

| Skill | Purpose |
|---|---|
| `query_router` | Classify intent (`knowledge` / `protocol` / `troubleshoot` / `hybrid` / `comparison`) with an ambiguity fallback |

Before this phase runs, `rag_app/agent/query.py::rewrite_query_with_pubmed`
issues a single small-LLM call that produces:

- `rewritten`: a coreference-resolved retrieval-friendly rewrite
- `subquestions`: 0-3 atomic sub-questions for compound queries
- `pubmed_query` / `pubmed_queries`: PubMed Boolean queries (one per sub-question
  for compound; 1-2 variants for atomic)

These are stashed in the skill context so the retrieval skills don't repeat
the LLM round-trip.

## Phase 2 — retrieval + fusion

| Skill | Purpose |
|---|---|
| `pubmed_evidence` | Run candidate PubMed Boolean queries in parallel, fuse results via Reciprocal Rank Fusion (k=60), dedup by content (collapses Current-Protocols-style sister-journal duplicates) |
| `protocol_retrieval` | LanceDB retrieval over `protocols/*.skill.md` with method-aware filtering, optional sub-question union, and cross-encoder rerank |
| `evidence_grading` | Cross-encoder rerank PubMed pool; quality labels (high/medium/low); per-sub-question coverage promotion that guarantees ≥2 papers per sub-question in the kept set |
| `answer_directive` | Build the per-turn instruction block that tunes the answer LLM's tone, structure, and table/list rules based on intent + evidence quality |
| `evidence_fusion` | Concatenate ranked PubMed + protocol context + sub-question directives + a STRICT citation-format directive into the final evidence block sent to the answer LLM |

## Post-generation

| Step | Purpose |
|---|---|
| Citation linkifier (`rag_backend/domain/citation_service.py`) | Convert numeric `[N]` citations in the answer into hyperlinks pointing at the cited PMIDs |
| Citation faithfulness verifier (`rag_app/agent/citation_verify.py`) | One small-LLM call that judges every (claim, abstract) pair as `supported` / `partial` / `unsupported`; surfaced to the UI as colored badges on each `[N]` |
| Telemetry rollup (`rag_backend/domain/telemetry_service.py`) | Per-turn observation logged server-side; not user-facing |

## Adding a new skill

1. Implement a class with `name: str` and `run(self, ctx, **kwargs) -> dict` in `rag_app/skills/`.
2. Register it in `rag_app/runner/orchestrator.py::ChatOrchestrator.__init__`.
3. Wire its inputs/outputs from sibling skills via `ctx.state` (read upstream
   keys, write your own).
4. The streaming SSE protocol does not have to change — additional skills
   can be slotted in without touching `rag_backend/api/routes_chat_stream.py`
   unless a brand-new SSE event is needed.

The orchestrator entry points (`route_question`, `retrieve_and_fuse`,
`run_turn`) are unit-test friendly — they take plain dict configs and return
plain dataclasses, with no FastAPI dependency.
