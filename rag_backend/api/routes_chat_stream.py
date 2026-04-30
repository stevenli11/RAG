"""Streaming chat route using Server-Sent Events (SSE).

Unlike ``POST /chat/turn`` which returns the full response in one shot, this
endpoint streams the LLM tokens as they are produced, plus discrete metadata
events at each stage of the pipeline. Designed for the Next.js frontend and
other browser clients that want SSE updates.

## Event protocol

All events are SSE framed as ``event: <name>\\ndata: <json>\\n\\n``. The
client must union these cases; each field is documented at its ``yield``
site below.

- ``router``      — {intent, rewritten, subquestions}        (emitted once,  early)
- ``retrieval``   — {protocol_skill_files, pubmed_count,     (emitted once,  after retrieval)
                     quality_counts, rerank_status, sources_topk}
- ``token``       — {text}                                   (0..N times,    interleaved with answer)
- ``references``  — {references_used, references_all,        (emitted once,  after LLM completes)
                     answer_display}
- ``citations``   — {verdicts}                                (emitted once,  after references; best-effort)
- ``followups``   — {questions}                              (emitted once,  best-effort)
- ``done``        — {}                                       (always last on success)
- ``error``       — {message, stage}                         (terminal on failure)
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import threading
import time
from functools import lru_cache
from typing import Any, AsyncGenerator, Dict, Tuple

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from rag_app.config.settings import get_config
from rag_app.core.llm_setup import initialize_embeddings, initialize_llm
from rag_app.data.vectorstore import load_vectorstore
from rag_app.services import doc_ingest
from rag_backend.domain.chat_service import ChatService
from rag_backend.domain.telemetry_service import build_turn_observation, print_turn_observation

from .schemas import ChatTurnRequest

router = APIRouter(prefix="/chat", tags=["chat-stream"])


_TIMING_ENABLED = os.getenv("RAG_STREAM_TIMING", "0").strip() in {"1", "true", "yes", "on"}


def _log_timing(stage: str, elapsed: float) -> None:
    """Emit a timing line to stderr; gated on RAG_STREAM_TIMING env var.

    Used to debug TTFT regressions without polluting production logs. Prints
    like ``[stream-timing] route=4.02s`` so individual stage costs are easy
    to diff between runs (PubMed, protocol, LLM first-token, etc).
    """
    if _TIMING_ENABLED:
        print(f"[stream-timing] {stage}={elapsed:.2f}s", file=sys.stderr, flush=True)


@lru_cache(maxsize=1)
def _bootstrap() -> Tuple[Dict, object, object, object]:
    config = get_config()
    graph_llm, small_llm = initialize_llm(config)
    embeddings = initialize_embeddings(config)
    vectorstore = load_vectorstore(config, embeddings, collection_name=config.get("milvus_collection"))
    return config, graph_llm, small_llm, vectorstore


@lru_cache(maxsize=1)
def _chat_service() -> ChatService:
    return ChatService()


def _sse(event: str, payload: Dict[str, Any]) -> Dict[str, str]:
    """Build an sse-starlette event dict with JSON-encoded data."""
    return {"event": event, "data": json.dumps(payload, ensure_ascii=False)}


def _reference_dict(article: Dict[str, Any]) -> Dict[str, Any]:
    """Trim a PubMed article record to the fields the client actually needs."""
    return {
        "pmid": str(article.get("pmid") or ""),
        "title": str(article.get("title") or ""),
        "abstract": str(article.get("abstract") or ""),
        "journal": str(article.get("journal") or ""),
        "year": str(article.get("year") or ""),
        "authors": list(article.get("authors") or []),
        "affiliations": list(article.get("affiliations") or []),
    }


async def _run_stream(req: ChatTurnRequest) -> AsyncGenerator[Dict[str, str], None]:
    """Drive one streaming turn through the pipeline stages."""
    try:
        config, graph_llm, small_llm, vectorstore = _bootstrap()
    except Exception as e:
        yield _sse("error", {"message": f"Backend init failed: {e}", "stage": "bootstrap"})
        return

    service = _chat_service()
    chat_history = [m.model_dump() for m in req.chat_history]
    t_route_start = time.perf_counter()

    # ---- Stage 1a: route_question (rewrite + intent, ~2-3s) ------------
    # Emit ``router`` as soon as we know intent + rewritten query, BEFORE
    # the slow retrieval work. This drops time-to-first-SSE-event from the
    # ~20s full-pipeline wait down to a couple seconds — the UI can show
    # "Searching PubMed…" placeholders while retrieval runs.
    try:
        route = await asyncio.to_thread(
            service.route_question,
            config=config,
            question=req.question,
            chat_history=chat_history,
            small_llm=small_llm,
            session_id=req.session_id,
        )
    except Exception as e:
        yield _sse("error", {"message": f"Router failed: {e}", "stage": "router"})
        return
    _log_timing("route", time.perf_counter() - t_route_start)

    yield _sse(
        "router",
        {
            "intent": route.intent,
            "rewritten": route.rewritten_question,
            "subquestions": list(route.subquestions or []),
        },
    )

    # ---- Stage 1b: retrieval + grading + fusion ------------------------
    # PubMed and protocol retrieval run in parallel inside the orchestrator
    # (see ChatOrchestrator.retrieve_and_fuse) so the two IO-heavy stages
    # overlap instead of summing their latencies.
    t_retrieve_start = time.perf_counter()
    try:
        execution = await asyncio.to_thread(
            service.retrieve_and_fuse,
            route=route,
            question=req.question,
            small_llm=small_llm,
            vectorstore=vectorstore,
            retrieval_k=req.retrieval_k,
            pubmed_max_results=req.pubmed_max_results,
            max_context_chars=req.max_context_chars,
        )
    except Exception as e:
        yield _sse("error", {"message": f"Retrieval failed: {e}", "stage": "retrieval"})
        return
    _log_timing("retrieve_and_fuse", time.perf_counter() - t_retrieve_start)

    # ---- Stage 1c: inject user-uploaded document (if any) --------------
    # The client ships only ``session_id``; we look up the cached condensed
    # document server-side and prepend it to the evidence block so the LLM
    # treats the user's own numbers as the primary context. See
    # ``rag_app.services.doc_ingest`` for the full flow.
    user_doc_attached = False
    if req.session_id:
        sess = doc_ingest.get_session(req.session_id)
        if sess and sess.condensed:
            execution.evidence = (
                doc_ingest.render_user_doc_block(sess) + "\n" + (execution.evidence or "")
            )
            # Mark context as non-empty so the RAG path is used even when
            # protocol + PubMed retrieval both came back empty.
            if not (execution.context and execution.context.strip()):
                execution.context = execution.evidence
            user_doc_attached = True

    # Pre-compute sources_topk from docs so the client can render the
    # "Retrieved protocols" panel alongside tokens, not after completion.
    sources_topk: list[str] = []
    for doc in execution.docs[:5]:
        meta = getattr(doc, "metadata", {}) or {}
        label = str(
            meta.get("protocol_relpath")
            or meta.get("source")
            or meta.get("title")
            or "unknown_source"
        )
        if label not in sources_topk:
            sources_topk.append(label)

    yield _sse(
        "retrieval",
        {
            "protocol_skill_files": list(execution.protocol_skill_files or []),
            "pubmed_count": len(execution.pubmed_articles or []),
            "quality_counts": dict(execution.quality_counts or {}),
            "rerank_status": dict(execution.rerank_status or {}),
            "sources_topk": sources_topk,
            "user_doc_attached": user_doc_attached,
        },
    )

    # ---- Stage 2: stream LLM tokens ------------------------------------
    # LangChain's .stream() is synchronous, so we pull it in a thread and
    # hand chunks back to the async generator via a queue. This keeps the
    # event loop responsive for sse-starlette's ping/disconnect handling.
    answer_parts: list[str] = []
    queue: asyncio.Queue[tuple[str, Any]] = asyncio.Queue(maxsize=256)
    SENTINEL_DONE = ("done", None)
    stop_event = threading.Event()

    def _producer() -> None:
        # Time from producer entry to first chunk arrival pinpoints the
        # LLM's own TTFT (disambiguates from retrieval + queue overhead).
        first_chunk_logged = False
        t_producer_start = time.perf_counter()

        def _push(kind: str, payload: Any) -> bool:
            if stop_event.is_set():
                return False
            fut = asyncio.run_coroutine_threadsafe(queue.put((kind, payload)), loop)
            try:
                # Bound producer-side waiting so disconnect/cancel can't block forever.
                fut.result(timeout=1.0)
                return True
            except Exception:
                return False

        try:
            for chunk in service.stream_answer_tokens(
                execution=execution,
                question=req.question,
                small_llm=small_llm,
                graph_llm=graph_llm,
                chat_history=chat_history,
            ):
                if stop_event.is_set():
                    return
                if not first_chunk_logged:
                    _log_timing("llm_first_chunk", time.perf_counter() - t_producer_start)
                    first_chunk_logged = True
                if not _push("chunk", chunk):
                    return
            _log_timing("llm_total_gen", time.perf_counter() - t_producer_start)
            _push(SENTINEL_DONE[0], SENTINEL_DONE[1])
        except Exception as exc:  # surface LLM errors through the queue
            _push("error", exc)

    loop = asyncio.get_running_loop()
    producer_task = asyncio.create_task(asyncio.to_thread(_producer))

    try:
        while True:
            kind, payload = await queue.get()
            if kind == "chunk":
                text = str(payload)
                answer_parts.append(text)
                yield _sse("token", {"text": text})
            elif kind == "error":
                yield _sse("error", {"message": f"LLM stream failed: {payload}", "stage": "llm_stream"})
                return
            elif kind == "done":
                break
    finally:
        stop_event.set()
        # Ensure producer thread wrapper completes even if client disconnects.
        with_producer_timeout = 0.5
        try:
            await asyncio.wait_for(producer_task, timeout=with_producer_timeout)
        except (asyncio.TimeoutError, Exception):
            producer_task.cancel()

    answer_raw = "".join(answer_parts)

    # ---- Stage 3: finalize (citation extraction, linkification) --------
    try:
        finalized = await asyncio.to_thread(
            service.finalize_answer, execution=execution, answer_raw=answer_raw
        )
    except Exception as e:
        yield _sse("error", {"message": f"Finalize failed: {e}", "stage": "finalize"})
        return

    # If finalize appended a minimum-citation anchor, emit it as a trailing
    # token so the client's accumulated text stays in sync with answer_raw.
    anchor = str(finalized.get("appended_anchor") or "")
    if anchor:
        yield _sse("token", {"text": anchor})

    yield _sse(
        "references",
        {
            "references_used": [_reference_dict(a) for a in finalized["references_used"]],
            "references_all": [_reference_dict(a) for a in finalized["references_all"]],
            "answer_display": finalized["answer_display"],
        },
    )

    # ---- Stage 3.5: citation faithfulness verifier (best-effort) -------
    # ~1-1.5s extra small_llm call. Run after `references` is sent so the
    # UI can render the answer + cite popovers immediately, then upgrade
    # them with verdict badges when this event arrives.
    try:
        verdicts = await asyncio.to_thread(
            service.verify_answer_citations,
            answer_raw=finalized["answer_raw"],
            references_all=finalized["references_all"],
            small_llm=small_llm,
        )
    except Exception:
        verdicts = []
    yield _sse("citations", {"verdicts": list(verdicts or [])})

    # ---- Stage 4: follow-ups (optional, best-effort) -------------------
    if req.generate_followups:
        try:
            follow_ups = await asyncio.to_thread(
                service.generate_followups,
                question=req.question,
                answer_raw=finalized["answer_raw"],
                small_llm=small_llm,
                chat_history=chat_history,
            )
        except Exception:
            follow_ups = []
        yield _sse("followups", {"questions": list(follow_ups or [])})

    # ---- Telemetry (fire-and-forget, logged server-side only) ----------
    try:
        telemetry = build_turn_observation(
            question=req.question,
            docs=execution.docs,
            pubmed_articles=execution.pubmed_articles,
            answer_text=finalized["answer_raw"],
            display_text=finalized["answer_display"],
        )
        print_turn_observation(telemetry)
    except Exception:
        pass

    yield _sse("done", {})


@router.post("/turn/stream")
async def chat_turn_stream(req: ChatTurnRequest):
    """Stream one chat turn as Server-Sent Events.

    The response is ``text/event-stream``. Clients should use an SSE parser
    (e.g. ``eventsource-parser`` on the browser) and match the event types
    documented at the top of this module.
    """
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="question must be non-empty")

    # ping=15 keeps proxies (and our own keepalive heuristics) happy during
    # long LLM generations; sse-starlette emits a comment ping every N secs.
    return EventSourceResponse(_run_stream(req), ping=15)
