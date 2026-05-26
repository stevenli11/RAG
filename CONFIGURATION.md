# Configuration

## Security model

- LLM provider keys and `PUBMED_API_KEY` are **server-managed only**.
  They are read from the backend process environment (or `.env`) and are
  never exposed to the browser. The env var name `DASHSCOPE_API_KEY` is
  kept for backward compatibility but accepts any OpenAI-compatible
  provider's key — set `DASHSCOPE_API_BASE` to that provider's `/v1`
  endpoint.
- The frontend is a thin SSE consumer; it has no direct access to provider
  credentials.
- Users may optionally configure their own vector backend via env (LanceDB
  by default, Milvus/Zilliz supported as a legacy cloud fallback).

## Required env vars

Copy `.env.example` to `.env` at the project root:

```env
# LLM provider (any OpenAI-compatible endpoint).
# Env-var names are kept stable for backward compatibility.
DASHSCOPE_API_KEY=your_provider_key
DASHSCOPE_API_BASE=https://your-provider.example.com/v1

# PubMed (optional; raises rate limit if set)
PUBMED_API_KEY=

# Vector store (local-first by default)
VECTOR_BACKEND=lancedb
LANCEDB_PATH=./data/lancedb/bge-small-en-v1.5
LANCEDB_TABLE=protocols

# Embedding backend/model used for both ingestion and query-time retrieval.
EMBEDDING_BACKEND=local
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# Rerank backend:
# - none: skip rerank; fall back to LanceDB hybrid + keyword scoring
# - dashscope: use DashScopeRerank with RERANK_MODEL
# - local: use sentence-transformers CrossEncoder with LOCAL_RERANK_MODEL
RERANK_BACKEND=local
RERANK_MODEL=none
LOCAL_RERANK_MODEL=BAAI/bge-reranker-base

# Optional Milvus/Zilliz (if VECTOR_BACKEND=milvus)
MILVUS_URI=
MILVUS_USER=
MILVUS_PASSWORD=
MILVUS_TOKEN=
MILVUS_COLLECTION=
```

For the Next.js frontend, add `frontend_next/.env.local`:

```env
BACKEND_API_URL=http://127.0.0.1:8001
```

## Runtime

```bash
# Backend (terminal A) — do NOT use --reload (LRU caches misbehave on reload)
LANCEDB_TABLE=protocols uvicorn rag_backend.api.app:app \
  --host 127.0.0.1 --port 8001

# Frontend (terminal B)
cd frontend_next && npm install && npm run dev
```

## Optional debug switches

| Env var | Effect |
|---|---|
| `APP_DEBUG_PUBMED=1` | Print every PubMed ESearch URL + hit count to stderr |
| `APP_DEBUG_QUERY=1` | Print the small_llm raw response from `rewrite_query_with_pubmed` |
| `RAG_DEBUG_CONTEXT=1` | Dump the full evidence + instructions payload sent to the answer LLM into `debug/last_turn.md` |
| `RAG_STREAM_TIMING=1` | Print per-stage latency (route / retrieve / first-token / total) to stderr |
| `EMBEDDING_LOCAL_FILES_ONLY=1` | Force Hugging Face local embedding models to load from cache only |

## Notes

- `.env` is gitignored.
- For production, prefer deployment-time secret management (e.g. a vault or a
  cloud secret manager) over committing keys anywhere on disk.
- The LanceDB index lives under `data/lancedb/bge-small-en-v1.5/` and is
  gitignored — rebuild it with `python scripts/ingest_protocols_lancedb.py`
  after pulling new protocol files.
