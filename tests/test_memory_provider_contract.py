"""Contract tests for the upcoming MemoryProvider integration.

These tests intentionally avoid real LLM, PubMed, and vector-store calls. They
lock down the seams a MemoryProvider adapter should touch:

- request identity fields stay optional and backward-compatible;
- a no-op memory backend can be called without changing the answer path;
- streaming SSE frames remain JSON-valid when memory metadata is present;
- memory text never becomes PubMed citation numbering by accident.

Run with:
    python -m unittest tests.test_memory_provider_contract
"""

from __future__ import annotations

import importlib
import inspect
import json
import sys
import types
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from typing import Any

from rag_backend.api.schemas import ChatTurnRequest


IDENTITY_FIELDS = ("user_id", "project_id", "conversation_id")


def _model_field_names(model_cls: type[Any]) -> set[str]:
    """Support both Pydantic v1 (__fields__) and v2 (model_fields)."""
    fields = getattr(model_cls, "model_fields", None)
    if fields is not None:
        return set(fields.keys())
    return set(getattr(model_cls, "__fields__", {}).keys())


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def _module(name: str, **attrs: Any) -> types.ModuleType:
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    return module


class _Dummy:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> "_Dummy":
        return self

    def __or__(self, other: Any) -> Any:
        return other


class _DummyAPIRouter:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def post(self, *args: Any, **kwargs: Any) -> Any:
        def decorator(func: Any) -> Any:
            return func

        return decorator


class _DummyHTTPException(Exception):
    def __init__(self, status_code: int, detail: str = "") -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _stream_import_stubs() -> dict[str, types.ModuleType]:
    """Stubs enough optional runtime deps to import the streaming route."""
    core = _module("langchain_core")
    core.__path__ = []  # type: ignore[attr-defined]
    community = _module("langchain_community")
    community.__path__ = []  # type: ignore[attr-defined]
    return {
        "fastapi": _module(
            "fastapi",
            APIRouter=_DummyAPIRouter,
            HTTPException=_DummyHTTPException,
        ),
        "sse_starlette": _module("sse_starlette"),
        "sse_starlette.sse": _module("sse_starlette.sse", EventSourceResponse=_Dummy),
        "dashscope": _module("dashscope", api_key=""),
        "langchain_openai": _module("langchain_openai", ChatOpenAI=_Dummy),
        "langchain_community": community,
        "langchain_community.embeddings": _module(
            "langchain_community.embeddings",
            DashScopeEmbeddings=_Dummy,
        ),
        "langchain_milvus": _module("langchain_milvus", Milvus=_Dummy),
        "pymilvus": _module("pymilvus", MilvusClient=_Dummy),
        "langchain_core": core,
        "langchain_core.documents": _module("langchain_core.documents", Document=_Dummy),
        "langchain_core.messages": _module("langchain_core.messages", HumanMessage=_Dummy),
        "langchain_core.output_parsers": _module(
            "langchain_core.output_parsers",
            StrOutputParser=_Dummy,
        ),
        "langchain_core.prompts": _module(
            "langchain_core.prompts",
            ChatPromptTemplate=_Dummy,
        ),
    }


def _execution_with_pubmed(evidence: str = "") -> SimpleNamespace:
    return SimpleNamespace(
        rewritten_question="rewritten question",
        intent="knowledge",
        pubmed_articles=[
            {
                "pmid": "11111111",
                "title": "First PubMed paper",
                "abstract": "First evidence abstract.",
                "journal": "J Test",
                "year": "2024",
                "authors": ["A"],
                "affiliations": [],
            },
            {
                "pmid": "22222222",
                "title": "Second PubMed paper",
                "abstract": "Second evidence abstract.",
                "journal": "J Test",
                "year": "2025",
                "authors": ["B"],
                "affiliations": [],
            },
        ],
        pubmed_references=[],
        evidence_summary="",
        quality_counts={"high": 1},
        use_table=False,
        table_type="",
        table_label="",
        scaffold_name="",
        wetlab_mode=False,
        high_risk=False,
        guardrail_summary="",
        docs=[],
        protocol_skill_files=[],
        context=evidence or "Ranked PubMed evidence:\n[1] First paper",
        evidence=evidence or "Ranked PubMed evidence:\n[1] First paper",
        instructions="",
        rerank_status={},
        subquestions=[],
        objective_audit={"applied": False},
        memory={"provider": "noop", "retrieved": 0, "enabled": True},
    )


def _finalize_answer(execution: Any, answer_raw: str) -> dict[str, Any]:
    """Small copy of ChatService.finalize_answer without heavy LangChain imports."""
    from rag_backend.domain.citation_service import extract_cited_reference_indices, linkify_citations
    from rag_backend.domain.format_service import sanitize_nonstandard_citation_tags, soft_wrap_long_lines

    answer_raw = sanitize_nonstandard_citation_tags(answer_raw)
    answer_raw = soft_wrap_long_lines(answer_raw)
    cited_ids = extract_cited_reference_indices(answer_raw, max_index=len(execution.pubmed_articles))
    answer_display = linkify_citations(answer_raw, execution.pubmed_articles)
    return {
        "answer_raw": answer_raw,
        "answer_display": answer_display,
        "references_used": [
            execution.pubmed_articles[i - 1]
            for i in cited_ids
            if 1 <= i <= len(execution.pubmed_articles)
        ],
        "references_all": execution.pubmed_articles or [],
        "sources_topk": [],
        "appended_anchor": "",
        "rule_refs": {},
    }


class ChatTurnRequestMemoryContractTests(unittest.TestCase):
    def test_legacy_minimal_request_still_parses_with_defaults(self) -> None:
        req = ChatTurnRequest(question="What is Seahorse OCR?")

        self.assertEqual(req.question, "What is Seahorse OCR?")
        self.assertEqual(req.chat_history, [])
        self.assertEqual(req.retrieval_k, 12)
        self.assertEqual(req.pubmed_max_results, 20)
        self.assertEqual(req.max_context_chars, 8000)
        self.assertTrue(req.generate_followups)
        self.assertIsNone(req.session_id)

    def test_identity_fields_are_optional_and_preserved_once_declared(self) -> None:
        fields = _model_field_names(ChatTurnRequest)
        missing = [name for name in IDENTITY_FIELDS if name not in fields]
        if missing:
            self.skipTest(f"Memory identity fields not implemented yet: {missing}")

        legacy = ChatTurnRequest(question="legacy request")
        for name in IDENTITY_FIELDS:
            self.assertIsNone(getattr(legacy, name))

        req = ChatTurnRequest(
            question="new request",
            user_id="user-1",
            project_id="project-1",
            conversation_id="conversation-1",
        )
        self.assertEqual(req.user_id, "user-1")
        self.assertEqual(req.project_id, "project-1")
        self.assertEqual(req.conversation_id, "conversation-1")


class NoopMemoryProviderContractTests(unittest.IsolatedAsyncioTestCase):
    def _load_provider_class(self) -> type[Any]:
        try:
            module = importlib.import_module("rag_app.services.memory")
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest("rag_app.services.memory not implemented yet") from exc

        for name in ("NoopMemoryProvider", "NoOpMemoryProvider"):
            provider_cls = getattr(module, name, None)
            if provider_cls is not None:
                return provider_cls
        raise unittest.SkipTest("NoopMemoryProvider class not implemented yet")

    def _load_memory_types(self) -> tuple[type[Any], type[Any]]:
        try:
            module = importlib.import_module("rag_app.services.memory")
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest("rag_app.services.memory not implemented yet") from exc
        try:
            return module.MemoryScope, module.MemoryWrite
        except AttributeError as exc:
            raise unittest.SkipTest("MemoryScope/MemoryWrite not implemented yet") from exc

    async def test_noop_retrieve_and_write_are_empty_and_non_throwing(self) -> None:
        provider_cls = self._load_provider_class()
        MemoryScope, MemoryWrite = self._load_memory_types()
        provider = provider_cls()
        scope = MemoryScope.from_request(
            user_id="user-1",
            project_id="project-1",
            conversation_id="conversation-1",
        )

        memories = await _maybe_await(
            provider.retrieve(
                scope=scope,
                query="Does prior context change this answer?",
                memory_types=["user", "project", "task", "evidence"],
            )
        )
        self.assertIn(memories, (None, [], ()))

        result = await _maybe_await(
            provider.write(
                scope=scope,
                turn=MemoryWrite(
                    question="Question",
                    answer="Answer summary",
                    metadata={"source": "unit-test"},
                ),
            )
        )
        self.assertIsInstance(result, dict)
        self.assertFalse(result.get("stored", False))

    async def test_noop_backend_does_not_change_finalize_answer_path(self) -> None:
        provider_cls = self._load_provider_class()
        MemoryScope, MemoryWrite = self._load_memory_types()
        provider = provider_cls()
        execution = _execution_with_pubmed()
        scope = MemoryScope.from_request(
            user_id="user-1",
            project_id="project-1",
            conversation_id="conversation-1",
        )

        await _maybe_await(
            provider.retrieve(
                scope=scope,
                query="test query",
                memory_types=["project"],
            )
        )
        finalized = _finalize_answer(
            execution=execution,
            answer_raw="This claim is supported by the first paper [1].",
        )
        await _maybe_await(
            provider.write(
                scope=scope,
                turn=MemoryWrite(
                    question="Question",
                    answer=finalized["answer_raw"],
                    metadata={},
                ),
            )
        )

        self.assertEqual([ref["pmid"] for ref in finalized["references_used"]], ["11111111"])
        self.assertIn("https://pubmed.ncbi.nlm.nih.gov/11111111/", finalized["answer_display"])

    def test_local_render_neutralizes_numeric_citation_tokens(self) -> None:
        try:
            module = importlib.import_module("rag_app.services.memory")
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest("rag_app.services.memory not implemented yet") from exc

        provider = module.LocalMemoryProvider()
        rendered = provider.render([
            module.MemoryItem(
                id="m1",
                memory_type="project",
                content="Prior note [7] and grouped note [1, 2] should not look like PubMed cites.",
            )
        ])

        self.assertNotIn("[7]", rendered)
        self.assertNotIn("[1, 2]", rendered)
        self.assertIn("(memory ref 7)", rendered)
        self.assertIn("(memory ref 1, 2)", rendered)


class StreamingMemoryContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_streaming_sse_frames_stay_json_valid_with_memory_identity_fields(self) -> None:
        try:
            with patch.dict(sys.modules, _stream_import_stubs()):
                from rag_backend.api import routes_chat_stream as stream_route
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest(f"streaming route dependencies are not installed: {exc}") from exc

        class FakeService:
            def route_question(self, **_: Any) -> Any:
                return SimpleNamespace(
                    intent="knowledge",
                    rewritten_question="rewritten",
                    subquestions=["subquestion"],
                )

            def retrieve_and_fuse(self, **_: Any) -> Any:
                return _execution_with_pubmed()

            def stream_answer_tokens(self, **_: Any) -> Any:
                yield "A streamed answer with a PubMed citation [1]."

            def finalize_answer(self, *, execution: Any, answer_raw: str) -> dict[str, Any]:
                return _finalize_answer(execution=execution, answer_raw=answer_raw)

            def verify_answer_citations(self, **_: Any) -> list[dict[str, Any]]:
                return [{"n": 1, "status": "supported", "reason": "fake", "claim": "fake"}]

            def generate_followups(self, **_: Any) -> list[str]:
                return []

        original_bootstrap = stream_route._bootstrap
        original_chat_service = stream_route._chat_service
        original_build_turn_observation = stream_route.build_turn_observation
        original_print_turn_observation = stream_route.print_turn_observation
        stream_route._bootstrap = lambda: ({}, object(), object(), object())
        stream_route._chat_service = lambda: FakeService()
        stream_route.build_turn_observation = lambda **_: {}
        stream_route.print_turn_observation = lambda _: None
        try:
            payload: dict[str, Any] = {
                "question": "streaming memory contract",
                "chat_history": [],
                "generate_followups": False,
            }
            fields = _model_field_names(ChatTurnRequest)
            for name in IDENTITY_FIELDS:
                if name in fields:
                    payload[name] = f"{name}-value"
            req = ChatTurnRequest(**payload)

            events = [event async for event in stream_route._run_stream(req)]
        finally:
            stream_route._bootstrap = original_bootstrap
            stream_route._chat_service = original_chat_service
            stream_route.build_turn_observation = original_build_turn_observation
            stream_route.print_turn_observation = original_print_turn_observation

        event_names = [event["event"] for event in events]
        self.assertEqual(event_names[0], "router")
        self.assertIn("retrieval", event_names)
        self.assertIn("references", event_names)
        self.assertIn("citations", event_names)
        self.assertIn("memory", event_names)
        self.assertLess(event_names.index("citations"), event_names.index("memory"))
        self.assertLess(event_names.index("memory"), event_names.index("done"))
        self.assertEqual(event_names[-1], "done")

        for event in events:
            self.assertIsInstance(event.get("event"), str)
            payload = json.loads(event.get("data", "{}"))
            self.assertIsInstance(payload, dict)
            if event["event"] == "retrieval":
                self.assertIsInstance(payload.get("memory"), dict)
            if event["event"] == "memory":
                # Future memory events must remain normal SSE JSON objects,
                # not raw strings or Python reprs that break browser parsing.
                json.dumps(payload)
                self.assertIsInstance(payload.get("status"), dict)


class CitationIsolationContractTests(unittest.TestCase):
    def test_memory_block_does_not_create_or_renumber_pubmed_references(self) -> None:
        memory_block = (
            "Memory context:\n"
            "- Prior project note [7]: user prefers Seahorse explanations.\n"
            "- Prior task note [42]: do not repeat an old troubleshooting branch.\n\n"
            "Ranked PubMed evidence:\n[1] First paper\n[2] Second paper"
        )
        execution = _execution_with_pubmed(evidence=memory_block)

        finalized = _finalize_answer(
            execution=execution,
            answer_raw="The answer cites only the first PubMed paper [1].",
        )

        self.assertEqual([ref["pmid"] for ref in finalized["references_used"]], ["11111111"])
        self.assertEqual([ref["pmid"] for ref in finalized["references_all"]], ["11111111", "22222222"])
        self.assertIn("https://pubmed.ncbi.nlm.nih.gov/11111111/", finalized["answer_display"])
        self.assertNotIn("https://pubmed.ncbi.nlm.nih.gov/22222222/", finalized["answer_display"])
        self.assertNotIn("https://pubmed.ncbi.nlm.nih.gov/7/", finalized["answer_display"])
        self.assertNotIn("https://pubmed.ncbi.nlm.nih.gov/42/", finalized["answer_display"])


if __name__ == "__main__":
    unittest.main()
