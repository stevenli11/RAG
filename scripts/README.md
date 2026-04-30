# Scripts

Operational + evaluation scripts.

## Build the protocol index

```bash
python scripts/ingest_protocols_lancedb.py \
    --protocols-dir ./protocols \
    --db-path ./data/lancedb \
    --table protocols
```

What it does:
1. Walks every `*.skill.md` / `*.risk_registry.md` under `protocols/`.
2. Chunks each file (size=250, overlap=30).
3. Embeds chunks with DashScope `text-embedding-v4`.
4. Writes a LanceDB table + a Tantivy FTS (BM25) index on the chunk text.

Dry-run (chunk only, no embedding API calls):

```bash
python scripts/ingest_protocols_lancedb.py --dry-run
```

## Smoke-test retrieval

```bash
python scripts/demo_lancedb_retrieval.py "western blot stripping buffer"
python scripts/demo_lancedb_retrieval.py --k 8 "Seahorse FCCP titration"
```

Each hit prints its `protocol_relpath`, fused score, and a content snippet.

## Eval harness

```bash
python scripts/eval_harness.py \
    --api-url http://127.0.0.1:8001 \
    --report eval_baseline.md \
    --save-json eval_baseline.json
```

Reads `scripts/core_cases.yaml` by default — 9 cases over the 3 actively-
optimized methods (Western Blot, Seahorse, CRISPR-Cas9).

Useful flags:

| Flag | Effect |
|---|---|
| `--cases <path>` | Use a different fixture file |
| `--cases-extra <path>` | Merge a second fixture file in (deduped by id) |
| `--only id1,id2,...` | Run only the listed case IDs |
| `--fail-fast` | Stop after 3 consecutive runtime errors |
| `--strict` | Exit non-zero if any boolean check fails |

Per-case metrics include Recall@K, MRR@K, Hit@K, Subq F1, coverage rate,
faithfulness, cite_rate, and per-stage latency. See
`rag_app/eval/metrics.py` for definitions.

## SSE smoke test

```bash
python scripts/smoke_stream.py "your question here"
```

Connects to `/chat/turn/stream` and prints each SSE event as it arrives.
