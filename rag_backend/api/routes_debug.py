"""Debug and observability routes."""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, List, Tuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from rag_app.config.settings import get_config
from rag_app.core.llm_setup import initialize_embeddings, initialize_llm
from rag_app.data.vectorstore import load_vectorstore
from rag_app.runner.orchestrator import ChatOrchestrator

router = APIRouter(prefix="/debug", tags=["debug"])


class RetrievalDebugRequest(BaseModel):
    question: str
    retrieval_k: int = 12
    pubmed_max_results: int = 20
    max_context_chars: int = 8000


class RetrievalDebugResponse(BaseModel):
    rewritten_question: str
    intent: str
    protocol_skill_files: List[str] = Field(default_factory=list)
    source_labels: List[str] = Field(default_factory=list)
    pubmed_titles: List[str] = Field(default_factory=list)
    pubmed_count: int = 0
    quality_counts: Dict[str, int] = Field(default_factory=dict)
    rerank_status: Dict[str, object] = Field(default_factory=dict)
    instructions: str = ""


@lru_cache(maxsize=1)
def _bootstrap() -> Tuple[Dict, object, object, object]:
    config = get_config()
    graph_llm, small_llm = initialize_llm(config)
    embeddings = initialize_embeddings(config)
    vectorstore = load_vectorstore(config, embeddings, collection_name=config.get("milvus_collection"))
    return config, graph_llm, small_llm, vectorstore


@lru_cache(maxsize=1)
def _orchestrator() -> ChatOrchestrator:
    return ChatOrchestrator()


@router.post("/retrieval", response_model=RetrievalDebugResponse)
def debug_retrieval(req: RetrievalDebugRequest) -> RetrievalDebugResponse:
    try:
        config, _graph_llm, small_llm, vectorstore = _bootstrap()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backend init failed: {e}") from e

    result = _orchestrator().run_turn(
        config=config,
        question=req.question,
        chat_history=[],
        small_llm=small_llm,
        vectorstore=vectorstore,
        retrieval_k=req.retrieval_k,
        pubmed_max_results=req.pubmed_max_results,
        max_context_chars=req.max_context_chars,
    )
    labels = []
    for doc in result.docs[:10]:
        meta = getattr(doc, "metadata", {}) or {}
        labels.append(
            str(
                meta.get("protocol_relpath")
                or meta.get("source")
                or meta.get("title")
                or "unknown_source"
            )
        )
    return RetrievalDebugResponse(
        rewritten_question=result.rewritten_question,
        intent=result.intent,
        protocol_skill_files=result.protocol_skill_files,
        source_labels=labels,
        pubmed_titles=[str(a.get("title", "") or "") for a in result.pubmed_articles],
        pubmed_count=len(result.pubmed_articles),
        quality_counts=result.quality_counts,
        rerank_status=result.rerank_status,
        instructions=result.instructions,
    )
