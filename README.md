# Biomedical Research Agent

A biomedical research AI agent that turns natural-language questions about
wet-lab experiments and biomedical literature into structured, evidence-grounded
answers. The current implementation is a method-aware Retrieval-Augmented
Generation (RAG) system focused on wet-lab protocols and PubMed literature; the
roadmap extends the same text-to-text interface into omics and medical data
analysis.

## Why

Both wet-lab method design and omics-data analysis remain heavily dependent on
domain expertise and programming skill. Knowledge is scattered across SOPs,
papers, and tribal experience. This project unifies that flow behind a single
text-to-text interface so a researcher can move from question → grounded
diagnosis → optimization plan without context-switching between literature
search, protocol manuals, and statistical scripts.

## Architecture (current)

```
User question
   │
   ▼
┌────────────────────┐
│ Query Router       │  intent classification (knowledge / protocol /
│ + LLM rewrite      │  troubleshoot / hybrid / comparison) and
│ + sub-question     │  decomposition into atomic sub-questions
│   decomposition    │
└────────┬───────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ Parallel retrieval                                     │
│  • PubMed multi-query RRF fusion (≤6 candidate         │
│    Boolean queries, reciprocal rank fusion k=60)       │
│  • Local protocol skills via LanceDB +                 │
│    cross-encoder rerank                                │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────┐
│ Evidence grading   │  per-subquestion coverage floor +
│ + answer directive │  quality labels (high/medium/low)
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Streaming answer   │  SSE token stream + post-generation
│ + citation verify  │  faithfulness check (supported /
│                    │  partial / unsupported per cite)
└────────────────────┘
```

The orchestration layer is composed of small, swappable skills (`rag_app/skills/`):
`query_router`, `pubmed_evidence`, `protocol_retrieval`, `evidence_grading`,
`answer_directive`, `evidence_fusion`. Adding a new modality (e.g. an omics
preprocessing or modeling skill) means dropping in a new skill class — the
orchestrator and SSE protocol stay unchanged.

### Key design choices

- **Multi-query Boolean retrieval**. The router emits 1-N PubMed Boolean queries
  (one per sub-question for compound questions; OR-expanded synonyms within each
  AND clause). Results are merged via Reciprocal Rank Fusion so papers
  surfacing across multiple queries float to the top.
- **Per-subquestion coverage**. After cross-encoder reranking, a keyword-overlap
  pass guarantees each sub-question has ≥2 supporting papers in the kept set,
  preventing compound questions from collapsing into single-topic answers.
- **Citation faithfulness verifier**. After generation, every inline `[N]`
  citation is checked by a smaller LLM against the actual cited abstract;
  unsupported / partial cites are surfaced to the user as colored badges in
  the UI.
- **History compression**. Multi-turn conversations beyond 3 turns are
  compressed via small-LLM summarization (cached by content hash) so the
  rewriter still sees what the user has tried, ruled out, or confirmed.
- **Local-first vectors**. Protocol corpus lives in an embedded LanceDB index;
  the only cloud dependency on the retrieval critical path is the LLM API.

## Stack

| Layer | Stack |
|---|---|
| LLM | Any OpenAI-compatible chat endpoint via `langchain_openai.ChatOpenAI` — configurable model + base URL. See **Supported LLMs** below. |
| Embeddings + Rerank | Pluggable. Works with any OpenAI-compatible embeddings endpoint and any cross-encoder reranker; re-ingest the index after changing models. |
| Vector store | LanceDB (local, embedded) |
| Backend | FastAPI + sse-starlette (streaming SSE) |
| Frontend | Next.js 14 (App Router) + TypeScript |
| Literature | NCBI E-utilities (PubMed) |
| Eval | Custom harness with Recall@K / MRR@K / Hit@K / Subq-F1 / Coverage / Faithfulness / cite_rate |

### Supported LLMs

Anything that exposes an OpenAI-compatible `/v1/chat/completions` endpoint
plugs in by setting two env vars (`DASHSCOPE_API_KEY` + `DASHSCOPE_API_BASE`,
kept under those names for backward compatibility) and the model name in
`rag_app/core/llm_setup.py`:

| Provider | Example models (current generation) | Base URL |
|---|---|---|
| **OpenAI** | `gpt-5.5`, `gpt-5.5-pro` | `https://api.openai.com/v1` |
| **Anthropic Claude** | `claude-opus-4-7`, `claude-sonnet-4-6`, `claude-haiku-4-5` | Native API, or via OpenRouter / proxy for OpenAI-compatible access |
| **DeepSeek** | `deepseek-v4-pro`, `deepseek-v4-flash` (legacy `deepseek-chat` / `deepseek-reasoner` retiring 2026-07-24) | `https://api.deepseek.com/v1` |
| **Alibaba Qwen / DashScope** | `qwen3.6-max-preview`, `qwen3.6-plus`, `qwen3.6-flash` | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| **Moonshot (Kimi)** | `kimi-k2.6`, `kimi-k2.5` | `https://api.moonshot.cn/v1` |
| **Google Gemini** | `gemini-3.1-pro`, `gemini-3-flash` | Via OpenAI-compatible gateway (e.g. OpenRouter) |
| **Zhipu / GLM** | `glm-5.1`, `glm-5` | `https://open.bigmodel.cn/api/paas/v4` |
| **Xiaomi MiMo** | `mimo-v2.5-pro`, `mimo-v2-pro`, `mimo-v2-flash` | `https://api.xiaomimimo.com/v1` |
| **OpenRouter** | any model in their catalog (cross-provider) | `https://openrouter.ai/api/v1` |

> Model names move fast. The list above shows representative current-
> generation choices — in practice any chat model the provider exposes
> through their OpenAI-compatible endpoint will work. Check the provider's
> own docs for the exact aliases and pricing tiers before locking one in.

The two-LLM split (one strong model for answer generation, one cheaper /
faster model for routing + grading + verification) is independent of the
provider — pick any combination across rows above.

## Layout

```
rag_app/                  Core business logic (LLM-agnostic)
  ├─ agent/               Query rewriting, citation verification
  ├─ skills/              Skill registry + orchestration units
  ├─ services/            PubMed client, history compression, doc ingest
  ├─ runner/              ChatOrchestrator (two-phase: route → retrieve+fuse)
  ├─ eval/                Quantitative metrics (Recall@K, MRR@K, faithfulness, ...)
  └─ data/                Vectorstore loaders

rag_backend/
  ├─ api/                 FastAPI routes (/chat/turn, /chat/turn/stream, /debug/retrieval)
  └─ domain/              Service layer: ChatService, citation linkifier, telemetry

frontend_next/            Next.js UI: streaming SSE consumer, inspector panel,
                          citation popovers with verdict badges

protocols/                Method skill files (Markdown). The 3 actively
                          prompt-optimized methods on the retrieval allow-list:
                            • western_blot.risk_registry.md
                            • Seahorse Real-Time Cell Metabolic Analysis.skill.md
                            • CRISPR-Cas9.skill.md

scripts/                  ingest_protocols_lancedb.py · eval_harness.py
                          · core_cases.yaml
                          · demo_lancedb_retrieval.py · smoke_stream.py
```

## Running locally

### Prerequisites

- Python 3.10+
- Node.js 22 (the frontend is pinned to Node 22; Node 25 has a known issue)
- An OpenAI-compatible LLM API key (the env var is named `DASHSCOPE_API_KEY`
  for historical reasons but accepts any OpenAI-compatible provider — set
  `DASHSCOPE_API_BASE` to that provider's `/v1` endpoint)
- Optional: PubMed API key (`PUBMED_API_KEY`) for higher rate limits

### 1. Environment

Copy `.env.example` to `.env` and fill in:

```env
# LLM (OpenAI-compatible). The env-var names are kept stable for backward
# compatibility — point base URL at whichever provider you use.
DASHSCOPE_API_KEY=your_provider_key
DASHSCOPE_API_BASE=https://your-provider.example.com/v1

PUBMED_API_KEY=
VECTOR_BACKEND=lancedb
LANCEDB_PATH=./data/lancedb/bge-small-en-v1.5
LANCEDB_TABLE=protocols
EMBEDDING_BACKEND=local
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
RERANK_BACKEND=local
RERANK_MODEL=none
LOCAL_RERANK_MODEL=BAAI/bge-reranker-base
```

For the frontend, create `frontend_next/.env.local`:

```env
BACKEND_API_URL=http://127.0.0.1:8001
```

### 2. Build the protocol index

```bash
pip install -r requirements.txt
python scripts/ingest_protocols_lancedb.py \
  --protocols-dir ./protocols \
  --db-path ./data/lancedb/bge-small-en-v1.5 \
  --table protocols \
  --embedder local \
  --model BAAI/bge-small-en-v1.5
```

The first local run downloads the BGE embedding model from Hugging Face; later
runs use the local cache. If the model is already cached and you are offline,
set `EMBEDDING_LOCAL_FILES_ONLY=1`.

### 3. Start the backend (terminal A)

```bash
LANCEDB_TABLE=protocols uvicorn rag_backend.api.app:app \
  --host 127.0.0.1 --port 8001
```

Note: do **not** use `--reload` — the LRU caches over LLM/embeddings/vectorstore
get into a bad state on reload. Restart manually after code changes.

### 4. Start the frontend (terminal B)

```bash
cd frontend_next
npm install
npm run dev
```

Open http://127.0.0.1:3000.

## API surface

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/healthz` | Liveness probe |
| `POST` | `/chat/turn` | Synchronous turn — returns full structured response |
| `POST` | `/chat/turn/stream` | Server-Sent Events stream of `router` / `retrieval` / `token` / `references` / `citations` / `followups` / `done` events |
| `POST` | `/session/attach` | Attach a user-uploaded document (cached server-side, condensed and prepended as the highest-priority evidence) |
| `POST` | `/session/detach` | Drop the cached attachment |
| `POST` | `/debug/retrieval` | Inspect routing, retrieved sources, PubMed candidate queries, rerank status, instructions block |

## Evaluation

The repo includes a quantitative eval harness:

```bash
python scripts/eval_harness.py \
  --api-url http://127.0.0.1:8001 \
  --report eval_baseline.md \
  --save-json eval_baseline.json
```

Default fixture: `scripts/core_cases.yaml` — 9 cases over the 3 actively-
optimized methods (Western Blot, Seahorse, CRISPR-Cas9). Pass your own YAML
via `--cases <path>` or layer additional cases on top with
`--cases-extra <path>`.

Metrics computed per case (see `rag_app/eval/metrics.py`):

| Metric | What it measures |
|---|---|
| Recall@K | Fraction of expected keyword groups satisfied by top-K PubMed retrieval |
| MRR@K | Mean reciprocal rank of the first paper matching any expected group |
| Hit@K | Whether top-K contains at least one matching paper |
| Subq F1 | Token-level F1 between predicted vs golden sub-question decomposition |
| Coverage rate | Fraction of sub-questions that have ≥2 cited refs whose text overlaps the sub-question's keywords |
| Faithfulness | Verifier-judged supported-vs-unsupported ratio over inline `[N]` citations (penalized to 0 when citations are required but absent) |
| cite_rate | Fraction of cases whose answer contains ≥1 numeric inline citation |

Reports break out per-tier (core / extended), per-bucket (precise / semantic /
compound / troubleshoot), and per-case.

## Roadmap

- **More method skills**: prompt-optimize the remaining unoptimized skill
  files and add them to the retrieval allow-list.
- **Failure-mode registries**: per-method `*.failure_modes.md` capturing
  known false-positive / false-negative patterns and how to discriminate them.
- **Objective audit skill**: a small reasoning step that, before recommending
  optimizations on user-uploaded experimental results, evaluates whether the
  user's data is itself reliable based on method failure-mode knowledge.
- **Omics + medical data analysis**: extend the same orchestrator with skills
  for data preprocessing (normalization, ssGSEA), feature selection (Cox,
  differential analysis), and modeling (Cox, GBM, RSF) — exposed through the
  same text-to-text interface.

## License

MIT (see LICENSE).
