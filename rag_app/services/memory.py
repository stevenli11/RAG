"""Minimal Agent Memory adapter surface.

This module intentionally does not integrate a real memory backend yet. It
defines the interface the RAG pipeline can call today, plus no-op and local
in-process stubs that make future ClaudeMemProvider wiring a backend swap
instead of a pipeline rewrite.
"""

from __future__ import annotations

import os
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from threading import Lock
from typing import Any, Dict, List, Optional, Protocol


@dataclass(frozen=True)
class MemoryScope:
    """Stable identifiers used to isolate memory retrieval and writes."""

    user_id: str = ""
    project_id: str = ""
    conversation_id: str = ""
    session_id: str = ""
    task_id: str = ""

    @classmethod
    def from_request(
        cls,
        *,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> "MemoryScope":
        return cls(
            user_id=(user_id or "").strip(),
            project_id=(project_id or "").strip(),
            conversation_id=(conversation_id or "").strip(),
            session_id=(session_id or "").strip(),
            task_id=(task_id or "").strip(),
        )

    def enabled(self) -> bool:
        return bool(self.user_id or self.project_id or self.conversation_id or self.session_id)

    def as_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class MemoryItem:
    """One retrieved memory entry rendered into answer context later."""

    id: str
    memory_type: str
    content: str
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MemoryWrite:
    """A best-effort write request emitted after a chat turn completes."""

    question: str
    answer: str
    rewritten_question: str = ""
    intent: str = ""
    subquestions: List[str] = field(default_factory=list)
    references: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryProvider(Protocol):
    """Backend contract for future local, ClaudeMem, or hosted memory stores."""

    name: str

    def retrieve(
        self,
        *,
        scope: MemoryScope,
        query: str,
        rewritten_query: str = "",
        memory_types: Optional[List[str]] = None,
        limit: int = 6,
    ) -> List[MemoryItem]:
        ...

    def render(self, items: List[MemoryItem]) -> str:
        ...

    def write(self, *, scope: MemoryScope, turn: MemoryWrite) -> Dict[str, Any]:
        ...


class NoOpMemoryProvider:
    """Safe default: pipeline calls succeed but no memory is read or written."""

    name = "noop"

    def retrieve(
        self,
        *,
        scope: MemoryScope,
        query: str,
        rewritten_query: str = "",
        memory_types: Optional[List[str]] = None,
        limit: int = 6,
    ) -> List[MemoryItem]:
        return []

    def render(self, items: List[MemoryItem]) -> str:
        return ""

    def write(self, *, scope: MemoryScope, turn: MemoryWrite) -> Dict[str, Any]:
        return {"provider": self.name, "stored": False, "reason": "noop"}


class LocalMemoryProvider:
    """Tiny in-process stub for integration tests and early UI plumbing.

    It is deliberately simple and volatile. Do not treat it as durable user
    memory; use it only to prove the adapter points work before adding a real
    ClaudeMemProvider or database-backed implementation.
    """

    name = "local"

    def __init__(self) -> None:
        self._items: List[tuple[MemoryScope, MemoryItem]] = []
        self._lock = Lock()

    def retrieve(
        self,
        *,
        scope: MemoryScope,
        query: str,
        rewritten_query: str = "",
        memory_types: Optional[List[str]] = None,
        limit: int = 6,
    ) -> List[MemoryItem]:
        if not scope.enabled():
            return []

        wanted = {m.strip().lower() for m in (memory_types or []) if m}
        query_text = f"{query} {rewritten_query}".lower()
        query_terms = {t for t in query_text.replace("/", " ").split() if len(t) >= 3}

        matches: List[MemoryItem] = []
        with self._lock:
            for item_scope, item in reversed(self._items):
                if wanted and item.memory_type.lower() not in wanted:
                    continue
                if not self._scope_matches(scope, item_scope):
                    continue
                content_terms = {t for t in item.content.lower().split() if len(t) >= 3}
                overlap = len(query_terms & content_terms)
                scored = MemoryItem(
                    id=item.id,
                    memory_type=item.memory_type,
                    content=item.content,
                    score=float(overlap),
                    metadata=dict(item.metadata),
                )
                matches.append(scored)

        matches.sort(key=lambda i: (i.score, i.metadata.get("created_at", 0)), reverse=True)
        return matches[: max(0, limit)]

    def render(self, items: List[MemoryItem]) -> str:
        if not items:
            return ""
        lines = [
            "Agent memory context (retrieved from prior user/project/task state):",
            "Use this as background context, but do not cite it as PubMed evidence.",
        ]
        for item in items:
            label = item.memory_type or "memory"
            content = _neutralize_numeric_citations(item.content)
            lines.append(f"- ({label}) {content}")
        return "\n".join(lines)

    def write(self, *, scope: MemoryScope, turn: MemoryWrite) -> Dict[str, Any]:
        if not scope.enabled():
            return {"provider": self.name, "stored": False, "reason": "empty_scope"}

        content_parts = [turn.question.strip(), turn.answer.strip()]
        content = "\n\n".join(p for p in content_parts if p)
        if not content:
            return {"provider": self.name, "stored": False, "reason": "empty_turn"}

        item = MemoryItem(
            id=uuid.uuid4().hex,
            memory_type="task",
            content=content[:4000],
            metadata={
                "created_at": time.time(),
                "intent": turn.intent,
                "rewritten_question": turn.rewritten_question,
                "subquestions": list(turn.subquestions or []),
                "reference_count": len(turn.references or []),
                **dict(turn.metadata or {}),
            },
        )
        with self._lock:
            self._items.append((scope, item))
        return {"provider": self.name, "stored": True, "item_id": item.id}

    @staticmethod
    def _scope_matches(requested: MemoryScope, stored: MemoryScope) -> bool:
        shared_identifier = False
        for field_name in ("user_id", "project_id", "conversation_id", "session_id", "task_id"):
            requested_value = getattr(requested, field_name)
            stored_value = getattr(stored, field_name)
            if requested_value and stored_value:
                shared_identifier = True
            if requested_value and stored_value and requested_value != stored_value:
                return False
        return shared_identifier


_LOCAL_PROVIDER = LocalMemoryProvider()
_NOOP_PROVIDER = NoOpMemoryProvider()


def _neutralize_numeric_citations(text: str) -> str:
    """Avoid making memory notes look like PubMed citation slots.

    The answer prompt reserves numeric ``[N]`` tokens for PubMed evidence.
    Memory is useful context, but it must not introduce citation-like tokens
    the LLM can copy into the final answer as if they were PubMed references.
    """
    return re.sub(r"\[(\d+(?:\s*,\s*\d+)*)\]", r"(memory ref \1)", text or "")


def get_memory_provider(config: Optional[Dict[str, Any]] = None) -> MemoryProvider:
    """Return the configured memory provider.

    Supported stubs:
    - ``noop``: default, fully reversible and side-effect free.
    - ``local``: process-local volatile store for wiring tests.

    A future ``claude_mem`` value should return a ClaudeMemProvider that
    implements the same interface without changing the RAG pipeline again.
    """

    config = config or {}
    provider = (
        os.getenv("RAG_MEMORY_PROVIDER")
        or str(config.get("memory_provider") or config.get("agent_memory_provider") or "")
        or "noop"
    ).strip().lower()

    if provider in {"local", "inmemory", "in-memory"}:
        return _LOCAL_PROVIDER
    return _NOOP_PROVIDER
