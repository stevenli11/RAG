"""Chat routes for backend API."""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, Tuple

from fastapi import APIRouter, HTTPException

from rag_app.config.settings import get_config
from rag_app.core.llm_setup import initialize_embeddings, initialize_llm
from rag_app.data.vectorstore import load_vectorstore
from rag_app.services.memory import MemoryScope
from rag_backend.domain.chat_service import ChatService
from rag_backend.domain.telemetry_service import print_turn_observation

from .schemas import (
    ChatTurnRequest,
    ChatTurnResponse,
    CitationVerdict,
    ReferenceItem,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@lru_cache(maxsize=1)
def _bootstrap() -> Tuple[Dict, object, object, object]:
    """Initialize shared runtime objects once per process."""
    config = get_config()
    graph_llm, small_llm = initialize_llm(config)
    embeddings = initialize_embeddings(config)
    vectorstore = load_vectorstore(config, embeddings, collection_name=config.get("milvus_collection"))
    return config, graph_llm, small_llm, vectorstore


@lru_cache(maxsize=1)
def _chat_service() -> ChatService:
    return ChatService()


def _dump_chat_message(message) -> dict:
    if hasattr(message, "model_dump"):
        return message.model_dump()
    return message.dict()


@router.post("/turn", response_model=ChatTurnResponse)
def chat_turn(req: ChatTurnRequest) -> ChatTurnResponse:
    try:
        config, graph_llm, small_llm, vectorstore = _bootstrap()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend init failed: {e}") from e

    service = _chat_service()
    memory_scope = MemoryScope.from_request(
        user_id=req.user_id,
        project_id=req.project_id,
        conversation_id=req.conversation_id,
        session_id=req.session_id,
        task_id=req.task_id,
    )
    result = service.run_turn(
        config=config,
        question=req.question,
        chat_history=[_dump_chat_message(m) for m in req.chat_history],
        small_llm=small_llm,
        graph_llm=graph_llm,
        vectorstore=vectorstore,
        retrieval_k=req.retrieval_k,
        pubmed_max_results=req.pubmed_max_results,
        max_context_chars=req.max_context_chars,
        generate_followups=req.generate_followups,
        session_id=req.session_id,
        memory_scope=memory_scope,
        memory_enabled=req.memory_enabled,
    )
    print_turn_observation(result.telemetry)
    return ChatTurnResponse(
        answer_markdown=result.answer_display,
        references_used=[ReferenceItem(**a) for a in result.references_used],
        references_all=[ReferenceItem(**a) for a in result.references_all],
        sources_topk=result.sources_topk,
        follow_up_questions=result.follow_up_questions,
        telemetry=result.telemetry,
        intent=result.execution.intent,
        rewritten_question=result.execution.rewritten_question,
        subquestions=list(result.execution.subquestions or []),
        citation_verdicts=[CitationVerdict(**v) for v in (result.citation_verdicts or [])],
        quality_counts=dict(result.execution.quality_counts or {}),
        rerank_status=dict(result.execution.rerank_status or {}),
        protocol_skill_files=list(result.execution.protocol_skill_files or []),
        timings=dict(result.timings or {}),
        objective_audit=dict(result.execution.objective_audit or {"applied": False}),
        rule_refs=dict(result.rule_refs or {}),
        memory=dict(result.memory or {}),
    )
