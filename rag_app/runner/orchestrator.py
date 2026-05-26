"""Orchestrator that executes skill pipeline for each chat turn."""

from __future__ import annotations

import datetime as _dt
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from rag_app.agent.query import _detect_active_method_context, rewrite_query_with_pubmed
from rag_app.services import doc_ingest
from rag_app.services.memory import MemoryProvider, MemoryScope
from rag_app.skills import (
    AnswerDirectiveSkill,
    EvidenceGradingSkill,
    EvidenceFusionSkill,
    ObjectiveAuditSkill,
    ProtocolRetrievalSkill,
    PubmedEvidenceSkill,
    QueryRouterSkill,
    SkillContext,
    SkillRegistry,
)


def _maybe_dump_context(
    *,
    question: str,
    rewritten: str,
    intent: str,
    instructions: str,
    evidence: str,
    pubmed_refs: List[str],
    protocol_skill_files: List[str],
) -> None:
    """Write the exact payload that will be handed to the answer LLM.

    Gated on ``RAG_DEBUG_CONTEXT=1`` so it's a no-op in normal runs. We keep
    both a rolling ``last_turn.md`` (easy for ``cat``) and a timestamped copy
    so successive queries don't overwrite each other when you're debugging a
    false-negative / hedge. Writes are best-effort — any filesystem failure
    is swallowed, because the diagnostic must never break a live answer.
    """
    if os.getenv("RAG_DEBUG_CONTEXT", "0").strip() not in {"1", "true", "yes", "on"}:
        return

    try:
        debug_dir = Path(__file__).resolve().parents[2] / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")

        body = (
            f"# RAG turn dump @ {ts}\n"
            f"# Set RAG_DEBUG_CONTEXT=0 to disable.\n\n"
            f"## Question\n{question}\n\n"
            f"## Rewritten question\n{rewritten}\n\n"
            f"## Router intent\n{intent}\n\n"
            f"## Protocol skill files used\n"
            + ("\n".join(f"- {n}" for n in protocol_skill_files) or "- (none)")
            + "\n\n"
            f"## PubMed references emitted\n"
            + ("\n".join(f"- {r}" for r in pubmed_refs) or "- (none)")
            + "\n\n"
            f"## Instructions block (appended to SYSTEM_PROMPT)\n"
            f"```\n{instructions}\n```\n\n"
            f"## Evidence block (the HUMAN message payload)\n"
            f"```\n{evidence}\n```\n"
        )

        (debug_dir / "last_turn.md").write_text(body, encoding="utf-8")
        (debug_dir / f"turn_{ts}.md").write_text(body, encoding="utf-8")
    except Exception:
        # Diagnostics must never break a real turn.
        pass


@dataclass
class TurnExecutionResult:
    rewritten_question: str
    intent: str
    pubmed_articles: List[Dict[str, Any]]
    pubmed_references: List[str]
    evidence_summary: str
    quality_counts: Dict[str, int]
    use_table: bool
    table_type: str
    table_label: str
    scaffold_name: str
    wetlab_mode: bool
    high_risk: bool
    guardrail_summary: str
    docs: List[Any]
    protocol_skill_files: List[str]
    context: str
    evidence: str
    instructions: str
    rerank_status: Dict[str, Any]
    subquestions: List[str]
    objective_audit: Dict[str, Any]
    memory: Dict[str, Any]


@dataclass
class RouteResult:
    """Output of the first orchestrator phase (rewrite + routing).

    Carries everything needed to start the retrieval phase. Kept separate
    from ``TurnExecutionResult`` so the streaming route can emit a ``router``
    SSE event *before* the slow retrieval work begins.
    """

    rewritten_question: str
    intent: str
    ctx: SkillContext  # shared state for telemetry keys like pubmed_rerank
    subquestions: List[str]


class ChatOrchestrator:
    """Run query-routing + retrieval + fusion via registered skills."""

    def __init__(self) -> None:
        self.registry = SkillRegistry()
        self.registry.register(QueryRouterSkill())
        self.registry.register(PubmedEvidenceSkill())
        self.registry.register(ProtocolRetrievalSkill())
        self.registry.register(EvidenceGradingSkill())
        self.registry.register(AnswerDirectiveSkill())
        self.registry.register(ObjectiveAuditSkill())
        self.registry.register(EvidenceFusionSkill())

    # ------------------------------------------------------------------
    # Two-phase entry points (used by streaming route to emit early events)
    # ------------------------------------------------------------------

    def route_question(
        self,
        *,
        config: Dict[str, Any],
        question: str,
        chat_history: List[Dict[str, Any]],
        small_llm: Any,
        session_id: str | None = None,
        memory_scope: MemoryScope | None = None,
        memory_provider: MemoryProvider | None = None,
    ) -> RouteResult:
        """Phase 1: rewrite + classify intent. Typically 2–3s end-to-end.

        Streaming callers invoke this first so they can emit a ``router``
        SSE event within a couple seconds, rather than waiting for the full
        ~20s retrieval pipeline to finish before anything reaches the UI.

        Uses the combined ``rewrite_query_with_pubmed`` call which produces
        BOTH the retrieval rewrite and the PubMed Boolean query from a
        single small_llm round-trip. The PubMed query is stashed in
        ``ctx.state["_pubmed_query_hint"]`` so ``PubmedEvidenceSkill`` can
        skip its own LLM rewrite call on the retrieval critical path.
        """
        ctx = SkillContext(config=config, state={})
        user_doc_condensed = ""
        if session_id:
            try:
                sess = doc_ingest.get_session(session_id)
                if sess and sess.condensed:
                    user_doc_condensed = sess.condensed
            except Exception:
                user_doc_condensed = ""
        # Stash for downstream skills (ObjectiveAuditSkill in particular needs
        # to inspect the user's actual experimental numbers when deciding
        # whether to challenge the data instead of optimising on top of it).
        if user_doc_condensed:
            ctx.state["_user_doc_condensed"] = user_doc_condensed
        rewrite_result = rewrite_query_with_pubmed(
            question,
            chat_history=chat_history,
            small_llm=small_llm,
            user_doc_condensed=user_doc_condensed,
        )
        rewritten = rewrite_result["rewritten"]
        pubmed_query_hint = rewrite_result.get("pubmed_query") or ""
        pubmed_query_hints = list(rewrite_result.get("pubmed_queries") or [])
        subquestions = list(rewrite_result.get("subquestions") or [])
        if pubmed_query_hint:
            ctx.state["_pubmed_query_hint"] = pubmed_query_hint
        if pubmed_query_hints:
            ctx.state["_pubmed_query_hints"] = pubmed_query_hints
        if subquestions:
            ctx.state["_subquestions"] = subquestions

        memory_items = []
        memory_block = ""
        memory_status: Dict[str, Any] = {"provider": "none", "retrieved": 0, "enabled": False}
        if memory_provider and memory_scope and memory_scope.enabled():
            memory_status = {"provider": memory_provider.name, "retrieved": 0, "enabled": True}
            try:
                memory_items = memory_provider.retrieve(
                    scope=memory_scope,
                    query=question,
                    rewritten_query=rewritten,
                    memory_types=["user", "project", "task", "evidence"],
                    limit=6,
                )
                memory_block = memory_provider.render(memory_items)
                memory_status["retrieved"] = len(memory_items)
            except Exception as exc:
                memory_items = []
                memory_block = ""
                memory_status.update({"error": str(exc), "retrieved": 0})
        if memory_scope:
            ctx.state["_memory_scope"] = memory_scope.as_dict()
        if memory_items:
            ctx.state["_memory_items"] = [item.as_dict() for item in memory_items]
        if memory_block:
            ctx.state["_memory_block"] = memory_block
        ctx.state["_memory_status"] = memory_status

        # Carry-forward method context as a sticky-skill fallback for
        # ProtocolRetrievalSkill. Even when rewrite_query preserves the
        # method name in its output, retrieval is more robust if it ALSO
        # has the explicit list of method tokens (so e.g. a query that
        # only mentions "RIPA buffer" but had "western blot" in turn 1
        # still picks the WB skill).
        active_ctx = _detect_active_method_context(chat_history)
        if active_ctx["methods"]:
            ctx.state["_carried_methods"] = active_ctx["methods"]
        if active_ctx["cell_lines"]:
            ctx.state["_carried_cell_lines"] = active_ctx["cell_lines"]

        route = self.registry.run("query_router", ctx, question=rewritten or question)
        intent = str(route.get("intent", "knowledge"))
        return RouteResult(
            rewritten_question=rewritten,
            intent=intent,
            ctx=ctx,
            subquestions=subquestions,
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
        """Phase 2: retrieval (PubMed ‖ protocol) + grading + fusion.

        Runs PubMed and local protocol retrieval *in parallel* — they only
        depend on (rewritten, intent) and together dominate the turn's
        wall-clock. Grading + directive + fusion are cheap and run serially
        after both retrievals join.
        """
        ctx = route.ctx
        rewritten = route.rewritten_question
        intent = route.intent
        subquestions = list(route.subquestions or [])

        # ---- parallel retrieval --------------------------------------
        # Budget can't be computed until we know PubMed context length, so
        # protocol retrieval initially gets the full budget and is trimmed
        # later via the fusion step. (The skill itself only reads top-K
        # documents; its own ``max_context_chars`` is a soft cap.)
        if intent in {"protocol", "troubleshoot", "hybrid", "comparison"}:
            min_local_budget = min(max_context_chars, 3200)
        else:
            min_local_budget = min(max_context_chars, 1600)

        def _run_pubmed() -> Dict[str, Any]:
            return self.registry.run(
                "pubmed_evidence",
                ctx,
                question=question,
                rewritten_question=rewritten,
                small_llm=small_llm,
                max_results=pubmed_max_results,
            )

        def _run_protocol() -> Dict[str, Any]:
            return self.registry.run(
                "protocol_retrieval",
                ctx,
                vectorstore=vectorstore,
                query=rewritten or question,
                intent=intent,
                k=retrieval_k,
                # Use min_local_budget as the floor; final trim happens below.
                max_context_chars=max(min_local_budget, max_context_chars),
                subqueries=subquestions,
            )

        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="retrieve") as pool:
            fut_pubmed = pool.submit(_run_pubmed)
            fut_protocol = pool.submit(_run_protocol)
            pubmed = fut_pubmed.result()
            protocol = fut_protocol.result()

        pubmed_context_raw = str(pubmed.get("context", "") or "")
        max_pubmed_chars = max(0, max_context_chars - min_local_budget)
        pubmed_context_for_fusion = pubmed_context_raw[:max_pubmed_chars] if max_pubmed_chars else ""

        # ---- serial post-processing ---------------------------------
        graded = self.registry.run(
            "evidence_grading",
            ctx,
            question=question,
            articles=pubmed.get("articles", []),
            subquestions=subquestions,
        )
        ranked_articles = graded.get("ranked_articles", []) or pubmed.get("articles", [])

        directive = self.registry.run(
            "answer_directive",
            ctx,
            question=question,
            intent=intent,
            has_pubmed=bool(ranked_articles),
            quality_counts=graded.get("quality_counts", {}),
        )

        # Objective audit — runs only on troubleshoot/hybrid intents that
        # ALSO carry user data or an optimisation verb. Result is fed into
        # evidence_fusion which prepends it as a "validity check" block at
        # the top of the evidence so the answer LLM is forced to address
        # data reliability before recommending tweaks.
        audit = self.registry.run(
            "objective_audit",
            ctx,
            question=question,
            intent=intent,
            protocol_skill_files=protocol.get("protocol_skill_files", []) or [],
            small_llm=small_llm,
        )
        if audit.get("applied"):
            ctx.state["objective_audit"] = audit

        fused = self.registry.run(
            "evidence_fusion",
            ctx,
            pubmed_context=pubmed_context_for_fusion,
            graded_pubmed_context=graded.get("graded_pubmed_context", ""),
            local_context=protocol.get("local_context", ""),
            answer_directive=directive.get("answer_directive", ""),
            subquestions=subquestions,
            audit=audit if audit.get("applied") else None,
        )

        memory_block = str(ctx.state.get("_memory_block") or "").strip()
        if memory_block:
            fused["evidence"] = memory_block + "\n\n" + str(fused.get("evidence", "") or "")
            fused["context"] = memory_block + "\n\n" + str(fused.get("context", "") or "")

        _maybe_dump_context(
            question=question,
            rewritten=rewritten,
            intent=intent,
            instructions=str(fused.get("instructions", "") or ""),
            evidence=str(fused.get("evidence", "") or ""),
            pubmed_refs=list(pubmed.get("references", []) or []),
            protocol_skill_files=list(protocol.get("protocol_skill_files", []) or []),
        )

        return TurnExecutionResult(
            rewritten_question=rewritten,
            intent=intent,
            pubmed_articles=ranked_articles,
            pubmed_references=pubmed.get("references", []),
            evidence_summary=str(graded.get("evidence_summary", "")),
            quality_counts=graded.get("quality_counts", {}),
            use_table=bool(directive.get("use_table")),
            table_type="",
            table_label="",
            scaffold_name="",
            wetlab_mode=bool(directive.get("wetlab_mode")),
            high_risk=bool(directive.get("high_risk")),
            guardrail_summary="",
            docs=protocol.get("docs", []),
            protocol_skill_files=protocol.get("protocol_skill_files", []),
            context=fused.get("context", ""),
            evidence=fused.get("evidence", ""),
            instructions=fused.get("instructions", ""),
            rerank_status={
                "protocol": ctx.state.get("protocol_rerank", {}),
                "pubmed": ctx.state.get("pubmed_rerank", {}),
            },
            subquestions=subquestions,
            objective_audit=audit if isinstance(audit, dict) else {"applied": False},
            memory=dict(ctx.state.get("_memory_status") or {}),
        )

    # ------------------------------------------------------------------
    # Monolithic entry point — preserved for non-streaming callers.
    # ------------------------------------------------------------------

    def run_turn(
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
        session_id: str | None = None,
        memory_scope: MemoryScope | None = None,
        memory_provider: MemoryProvider | None = None,
    ) -> TurnExecutionResult:
        route = self.route_question(
            config=config,
            question=question,
            chat_history=chat_history,
            small_llm=small_llm,
            session_id=session_id,
            memory_scope=memory_scope,
            memory_provider=memory_provider,
        )
        return self.retrieve_and_fuse(
            route=route,
            question=question,
            small_llm=small_llm,
            vectorstore=vectorstore,
            retrieval_k=retrieval_k,
            pubmed_max_results=pubmed_max_results,
            max_context_chars=max_context_chars,
        )
