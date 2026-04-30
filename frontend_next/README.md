# Next.js Frontend (Streaming)

This is a minimal Next.js frontend for testing the RAG backend streaming API.

## 1) Start backend first

```bash
cd /Users/leven/Library/CloudStorage/OneDrive-TheOhioStateUniversityWexnerMedicalCenter/personal/Startup/RAG_local
uvicorn rag_backend.api.app:app --reload --port 8001
```

## 2) Start frontend

```bash
cd /Users/leven/Library/CloudStorage/OneDrive-TheOhioStateUniversityWexnerMedicalCenter/personal/Startup/RAG_local/frontend_next
cp .env.local.example .env.local
npm install
npm run dev
```

Open `http://127.0.0.1:3000`.

## Notes

- Browser calls go to Next API route `/api/chat/turn/stream`, then proxy to backend.
- This avoids CORS issues without modifying FastAPI middleware.
- Backend target is configured by `BACKEND_API_URL` in `.env.local`.

