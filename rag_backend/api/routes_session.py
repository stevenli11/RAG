"""Session-scoped document attachment endpoints.

POST /session/attach   — multipart upload, returns session_id + preview
POST /session/detach   — drop the cached document for a session_id
GET  /session/{id}     — return session metadata (debug / UI refresh)

The actual document text is cached on the backend (see
``rag_app.services.doc_ingest``); chat requests only carry ``session_id``
so per-turn payloads stay small. Session state lives in-memory only.
"""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from rag_app.services import doc_ingest

# Reuse the streaming route's cached bootstrap so we don't re-initialize
# the small LLM on every upload. Both routes want the same ``small_llm``.
from .routes_chat_stream import _bootstrap

router = APIRouter(prefix="/session", tags=["session"])


# Cap raw upload bytes to something sane for a medical/wetlab SOP doc.
# 5 MB is generous for a 30-page .docx with figures.
_MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@router.post("/attach")
async def attach_document(file: UploadFile = File(...)) -> dict:
    """Upload a document, condense it with small_llm, return session_id."""
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(data) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (>{_MAX_UPLOAD_BYTES // (1024 * 1024)} MB)",
        )

    try:
        raw = doc_ingest.parse_bytes(file.filename or "", data)
    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse failed: {e}")

    if not raw.strip():
        raise HTTPException(status_code=400, detail="No extractable text in document")

    try:
        _config, _graph_llm, small_llm, _vs = _bootstrap()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend init failed: {e}")

    condensed = doc_ingest.condense_document(raw, small_llm)
    session = doc_ingest.create_session(
        filename=file.filename or "untitled",
        raw=raw,
        condensed=condensed,
    )
    return session.to_public()


@router.post("/detach")
async def detach_document(payload: dict) -> dict:
    session_id = str(payload.get("session_id") or "").strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    removed = doc_ingest.delete_session(session_id)
    return {"removed": removed, "session_id": session_id}


@router.get("/{session_id}")
async def get_session_info(session_id: str) -> dict:
    sess = doc_ingest.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="session not found")
    return sess.to_public()


@router.get("/{session_id}/condensed")
async def get_condensed_text(session_id: str) -> dict:
    """Return the full condensed markdown for debugging.

    Lets the user eyeball what the small_llm compressed the document into
    — if their interpretation / categorization got dropped, this is where
    you'd catch it before it silently degrades downstream answers.
    """
    sess = doc_ingest.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="session not found")
    return {
        "session_id": sess.session_id,
        "filename": sess.filename,
        "raw_chars": sess.char_count,
        "condensed_chars": len(sess.condensed),
        "condensed": sess.condensed,
    }
