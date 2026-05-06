"""Pydantic request/response schemas for chat APIs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    user: str = ""
    assistant: str = ""


class ChatTurnRequest(BaseModel):
    question: str
    chat_history: List[ChatMessage] = Field(default_factory=list)
    retrieval_k: int = 12
    pubmed_max_results: int = 20
    max_context_chars: int = 8000
    generate_followups: bool = True
    # Optional: when set, backend looks up an uploaded document in the
    # in-memory session store and injects its condensed summary into the
    # evidence block as the highest-priority context. See
    # ``rag_app.services.doc_ingest``.
    session_id: Optional[str] = None


class ReferenceItem(BaseModel):
    pmid: str = ""
    title: str = ""
    abstract: str = ""
    journal: str = ""
    year: str = ""
    authors: List[str] = Field(default_factory=list)
    affiliations: List[str] = Field(default_factory=list)


class CitationVerdict(BaseModel):
    n: int
    status: str  # "supported" | "partial" | "unsupported"
    reason: str = ""
    claim: str = ""


class ChatTurnResponse(BaseModel):
    answer_markdown: str
    references_used: List[ReferenceItem] = Field(default_factory=list)
    references_all: List[ReferenceItem] = Field(default_factory=list)
    sources_topk: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
    telemetry: Dict[str, Any] = Field(default_factory=dict)
    intent: Optional[str] = None
    # Eval-friendly fields (added for the metric harness — non-streaming clients
    # previously only got the answer + references; the harness needs structured
    # access to decomposition + verifier output too).
    rewritten_question: str = ""
    subquestions: List[str] = Field(default_factory=list)
    citation_verdicts: List[CitationVerdict] = Field(default_factory=list)
    quality_counts: Dict[str, int] = Field(default_factory=dict)
    rerank_status: Dict[str, Any] = Field(default_factory=dict)
    protocol_skill_files: List[str] = Field(default_factory=list)
    timings: Dict[str, float] = Field(default_factory=dict)
    # ObjectiveAudit output (refuse-to-flatter signal). Empty/applied=False
    # for non-troubleshoot or non-optimisation turns.
    objective_audit: Dict[str, Any] = Field(default_factory=dict)

