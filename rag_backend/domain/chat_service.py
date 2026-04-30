"""UI-agnostic chat turn orchestration service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage

import time

from rag_app.agent.citation_verify import verify_citations
from rag_app.agent.query import create_rag_chain
from rag_app.runner.orchestrator import ChatOrchestrator, RouteResult, TurnExecutionResult
from rag_app.services.follow_up import generate_follow_up_questions

from .citation_service import extract_cited_reference_indices, linkify_citations
from .format_service import sanitize_nonstandard_citation_tags, soft_wrap_long_lines
from .telemetry_service import build_turn_observation


@dataclass
class ChatTurnResult:
    answer_raw: str
    answer_display: str
    references_used: List[Dict[str, Any]]
    references_all: List[Dict[str, Any]]
    sources_topk: List[str]
    follow_up_questions: List[str]
    telemetry: Dict[str, Any]
    execution: TurnExecutionResult
    # Added for the eval harness — captured from the same pipeline the
    # streaming route exposes via SSE. Backwards-compatible: existing
    # callers can ignore these.
    citation_verdicts: List[Dict[str, Any]] = None  # type: ignore[assignment]
    timings: Dict[str, float] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.citation_verdicts is None:
            self.citation_verdicts = []
        if self.timings is None:
            self.timings = {}


class ChatService:
    """Run one chat turn and return structured response for any frontend."""

    def __init__(self) -> None:
        self.orchestrator = ChatOrchestrator()

    # ------------------------------------------------------------------
    # Stage methods — used by both monolithic run_turn and streaming route
    # ------------------------------------------------------------------

    def route_question(
        self,
        *,
        config: Dict[str, Any],
        question: str,
        chat_history: List[Dict[str, Any]],
        small_llm: Any,
        session_id: str | None = None,
    ) -> RouteResult:
        """Phase 1: rewrite + intent classification (~2-3s).

        Streaming route calls this first so it can emit a ``router`` SSE
        event before the (slow) retrieval pipeline starts.
        """
        return self.orchestrator.route_question(
            config=config,
            question=question,
            chat_history=chat_history,
            small_llm=small_llm,
            session_id=session_id,
        )

    def retrieve_and_fuse(
        self,
        *,
        route: RouteResult,
        question: str,
        small_llm: Any,
        vectorstore: Any,
        retrieval_k: int,
        pubmed_max_results: int,
        max_context_chars: int,
    ) -> TurnExecutionResult:
        """Phase 2: parallel PubMed + protocol retrieval, then grading/fusion."""
        return self.orchestrator.retrieve_and_fuse(
            route=route,
            question=question,
            small_llm=small_llm,
            vectorstore=vectorstore,
            retrieval_k=retrieval_k,
            pubmed_max_results=pubmed_max_results,
            max_context_chars=max_context_chars,
        )

    def prepare_execution(
        self,
        *,
        config: Dict[str, Any],
        question: str,
        chat_history: List[Dict[str, Any]],
        small_llm: Any,
        vectorstore: Any,
        retrieval_k: int,
        pubmed_max_results: int,
        max_context_chars: int,
    ) -> TurnExecutionResult:
        """Legacy single-shot: route + retrieve + fuse in one call."""
        return self.orchestrator.run_turn(
            config=config,
            question=question,
            chat_history=chat_history,
            small_llm=small_llm,
            vectorstore=vectorstore,
            retrieval_k=retrieval_k,
            pubmed_max_results=pubmed_max_results,
            max_context_chars=max_context_chars,
        )

    def stream_answer_tokens(
        self,
        *,
        execution: TurnExecutionResult,
        question: str,
        small_llm: Any,
        graph_llm: Any,
        chat_history: List[Dict[str, Any]],
    ):
        """Stage 2 (streaming variant): yield answer tokens as they arrive.

        Generator yields plain ``str`` chunks. Caller is responsible for
        accumulating them into the final ``answer_raw`` for post-processing.
        """
        use_rag = bool(execution.context and execution.context.strip())
        if use_rag:
            rag_chain = create_rag_chain(
                graph_llm,
                question=question,
                small_llm=small_llm,
                chat_history=chat_history,
            )
            chain_input = {
                "evidence": execution.evidence,
                "instructions": execution.instructions,
                "question": question,
            }
            # StrOutputParser sits at the tail so ``.stream()`` yields str chunks.
            for chunk in rag_chain.stream(chain_input):
                if chunk:
                    yield str(chunk)
        else:
            direct_prompt = (
                "Please answer the following question based on your general "
                f"knowledge.\nQuestion: {question}"
            )
            for chunk in graph_llm.stream([HumanMessage(content=direct_prompt)]):
                text = getattr(chunk, "content", "") or ""
                if text:
                    yield str(text)

    def invoke_answer(
        self,
        *,
        execution: TurnExecutionResult,
        question: str,
        small_llm: Any,
        graph_llm: Any,
        chat_history: List[Dict[str, Any]],
    ) -> str:
        """Stage 2 (non-streaming variant): synchronous full answer."""
        use_rag = bool(execution.context and execution.context.strip())
        if use_rag:
            rag_chain = create_rag_chain(
                graph_llm,
                question=question,
                small_llm=small_llm,
                chat_history=chat_history,
            )
            chain_input = {
                "evidence": execution.evidence,
                "instructions": execution.instructions,
                "question": question,
            }
            return rag_chain.invoke(chain_input)
        direct_prompt = (
            "Please answer the following question based on your general "
            f"knowledge.\nQuestion: {question}"
        )
        msg = graph_llm.invoke([HumanMessage(content=direct_prompt)])
        return msg.content if hasattr(msg, "content") else str(msg)

    def finalize_answer(
        self,
        *,
        execution: TurnExecutionResult,
        answer_raw: str,
    ) -> Dict[str, Any]:
        """Stage 3: sanitise, wrap, extract citations, link, build references.

        Returns a dict with ``answer_raw``, ``answer_display`` (linkified),
        ``references_used``, ``references_all``, ``sources_topk``,
        ``appended_anchor`` (kept for API compatibility; always empty).
        """
        answer_raw = sanitize_nonstandard_citation_tags(answer_raw)
        answer_raw = soft_wrap_long_lines(answer_raw)
        cited_ids = extract_cited_reference_indices(answer_raw, max_index=len(execution.pubmed_articles))

        appended_anchor = ""

        answer_display = (
            linkify_citations(answer_raw, execution.pubmed_articles)
            if execution.pubmed_articles
            else answer_raw
        )

        references_used = [
            execution.pubmed_articles[i - 1]
            for i in cited_ids
            if 1 <= i <= len(execution.pubmed_articles)
        ]
        references_all = execution.pubmed_articles or []

        sources_topk: List[str] = []
        for doc in execution.docs[:5]:
            meta = getattr(doc, "metadata", {}) or {}
            label = meta.get("protocol_relpath") or meta.get("source") or meta.get("title") or "unknown_source"
            label = str(label)
            if label not in sources_topk:
                sources_topk.append(label)

        return {
            "answer_raw": answer_raw,
            "answer_display": answer_display,
            "references_used": references_used,
            "references_all": references_all,
            "sources_topk": sources_topk,
            "appended_anchor": appended_anchor,
        }

    def verify_answer_citations(
        self,
        *,
        answer_raw: str,
        references_all: List[Dict[str, Any]],
        small_llm: Any,
    ) -> List[Dict[str, Any]]:
        """Stage 3.5: post-generation citation faithfulness check.

        Returns a list of ``{n, status, reason, claim}`` entries per inline
        citation. Costs one extra small_llm call (~1-1.5s on qwen-flash) and
        is best-effort — any failure returns []. The streaming route emits
        these as a separate SSE event so the UI can badge unsupported cites
        without holding back the answer text.
        """
        try:
            return verify_citations(
                answer=answer_raw,
                references_used=[],
                references_all=references_all,
                small_llm=small_llm,
            )
        except Exception:
            return []

    def generate_followups(
        self,
        *,
        question: str,
        answer_raw: str,
        small_llm: Any,
        chat_history: List[Dict[str, Any]],
    ) -> List[str]:
        """Stage 4: generate follow-up questions (best-effort)."""
        if not small_llm:
            return []
        try:
            return generate_follow_up_questions(
                question=question,
                answer=answer_raw,
                small_llm=small_llm,
                max_questions=3,
                chat_history=chat_history,
            )
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Monolithic entrypoint — preserved for /chat/turn (non-streaming).
    # ------------------------------------------------------------------

    def run_turn(
        self,
        *,
        config: Dict[str, Any],
        question: str,
        chat_history: List[Dict[str, Any]],
        small_llm: Any,
        graph_llm: Any,
        vectorstore: Any,
        retrieval_k: int,
        pubmed_max_results: int,
        max_context_chars: int,
        generate_followups: bool = True,
    ) -> ChatTurnResult:
        # Per-stage timings — populated even on error paths so the eval
        # harness can detect "where the slow turn was slow".
        timings: Dict[str, float] = {}

        t0 = time.perf_counter()
        execution = self.prepare_execution(
            config=config,
            question=question,
            chat_history=chat_history,
            small_llm=small_llm,
            vectorstore=vectorstore,
            retrieval_k=retrieval_k,
            pubmed_max_results=pubmed_max_results,
            max_context_chars=max_context_chars,
        )
        timings["prepare"] = time.perf_counter() - t0

        t1 = time.perf_counter()
        answer_raw = self.invoke_answer(
            execution=execution,
            question=question,
            small_llm=small_llm,
            graph_llm=graph_llm,
            chat_history=chat_history,
        )
        timings["generate"] = time.perf_counter() - t1

        t2 = time.perf_counter()
        finalized = self.finalize_answer(execution=execution, answer_raw=answer_raw)
        answer_raw = finalized["answer_raw"]
        answer_display = finalized["answer_display"]
        timings["finalize"] = time.perf_counter() - t2

        # Citation faithfulness verification (matches the streaming route
        # behavior so non-streaming and streaming clients see consistent
        # verdicts; harness needs them for the faithfulness metric).
        t3 = time.perf_counter()
        verdicts = self.verify_answer_citations(
            answer_raw=answer_raw,
            references_all=finalized["references_all"],
            small_llm=small_llm,
        )
        timings["verify"] = time.perf_counter() - t3

        follow_ups: List[str] = []
        if generate_followups:
            t4 = time.perf_counter()
            follow_ups = self.generate_followups(
                question=question,
                answer_raw=answer_raw,
                small_llm=small_llm,
                chat_history=chat_history,
            )
            timings["followups"] = time.perf_counter() - t4

        telemetry = build_turn_observation(
            question=question,
            docs=execution.docs,
            pubmed_articles=execution.pubmed_articles,
            answer_text=answer_raw,
            display_text=answer_display,
        )

        timings["total"] = time.perf_counter() - t0

        return ChatTurnResult(
            answer_raw=answer_raw,
            answer_display=answer_display,
            references_used=finalized["references_used"],
            references_all=finalized["references_all"],
            sources_topk=finalized["sources_topk"],
            follow_up_questions=follow_ups,
            telemetry=telemetry,
            execution=execution,
            citation_verdicts=verdicts,
            timings=timings,
        )
