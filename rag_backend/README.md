# RAG Backend (UI-Agnostic)

This package contains the UI-agnostic backend services that power the
FastAPI + Next.js application.

## Run API

```bash
cd /Users/leven/Library/CloudStorage/OneDrive-TheOhioStateUniversityWexnerMedicalCenter/personal/Startup/RAG_local
uvicorn rag_backend.api.app:app --reload --port 8000
```

## Endpoints

- `GET /healthz`
- `POST /chat/turn`
- `POST /debug/retrieval`

## Example request

```bash
curl -X POST http://127.0.0.1:8000/chat/turn \
  -H "Content-Type: application/json" \
  -d '{
    "question": "western blot stripping buffer pH and incubation conditions",
    "chat_history": [],
    "retrieval_k": 12,
    "pubmed_max_results": 20,
    "max_context_chars": 8000
  }'
```
