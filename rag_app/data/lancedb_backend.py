"""LanceDB backend for protocol retrieval.

Drop-in replacement for the Milvus-based vectorstore. Exposes the same
`as_retriever(search_kwargs=...).invoke(query)` contract used by
``rag_app/skills/protocol_retrieval.py``, but runs fully local and supports
hybrid BM25 + vector retrieval out of the box.

Why: Milvus/Zilliz cloud is a hosted-only service; LanceDB is an embedded
columnar vector store (just files on disk) with native full-text search via
Tantivy. This lets us do BM25 + ANN + RRF fusion without standing up extra
infrastructure, which is the Phase-1 item in the local-first roadmap.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from langchain_core.documents import Document


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

DEFAULT_LANCEDB_PATH = "./data/lancedb"
DEFAULT_TABLE_NAME = "protocols"
# LanceDB full-text search column. BM25 is built on top of Tantivy.
_FTS_COLUMN = "text"
_VECTOR_COLUMN = "vector"
# Reciprocal rank fusion constant. 60 is the de-facto default from the
# original Cormack et al. paper and what LanceDB's RRFReranker ships with.
_RRF_K = 60


def _resolve_db_path(path: Optional[str]) -> str:
    raw = path or os.getenv("LANCEDB_PATH", DEFAULT_LANCEDB_PATH)
    return str(Path(raw).expanduser().resolve())


def _resolve_table_name(table: Optional[str]) -> str:
    return table or os.getenv("LANCEDB_TABLE", DEFAULT_TABLE_NAME)


def _list_tables(db: Any) -> List[str]:
    """Return the list of table names regardless of lancedb version.

    Recent lancedb ships ``list_tables`` returning a paginated
    ``TableNamesResult`` (with a ``tables`` attribute), while older versions —
    and the legacy ``table_names`` alias — return a plain ``list[str]``.
    Normalise both into ``list[str]`` so membership checks behave.
    """
    if hasattr(db, "list_tables"):
        result = db.list_tables()
        # Newer API returns an object with ``.tables``; older just returns a list.
        inner = getattr(result, "tables", result)
        return list(inner)
    # Legacy fallback (lancedb<0.13 style).
    return list(db.table_names())


# ---------------------------------------------------------------------------
# Retriever adapter
# ---------------------------------------------------------------------------


@dataclass
class _HybridSearchConfig:
    k: int = 8
    expr: Optional[str] = None
    # 0.0 = pure BM25, 1.0 = pure vector, in-between = linear mix (fallback).
    # When RRF is used this is ignored.
    vector_weight: float = 0.7
    use_rrf: bool = True


class LanceDBRetriever:
    """Hybrid retriever that matches the interface used by protocol_retrieval."""

    def __init__(
        self,
        *,
        table: Any,
        embeddings: Any,
        search_cfg: Optional[_HybridSearchConfig] = None,
    ) -> None:
        self._table = table
        self._embeddings = embeddings
        self._cfg = search_cfg or _HybridSearchConfig()

    def with_search_kwargs(self, search_kwargs: Optional[Dict[str, Any]]) -> "LanceDBRetriever":
        cfg = _HybridSearchConfig(**{**self._cfg.__dict__})
        if search_kwargs:
            if "k" in search_kwargs:
                cfg.k = int(search_kwargs["k"])
            # Translate Milvus-style expression to LanceDB SQL-ish filter.
            if "expr" in search_kwargs and search_kwargs["expr"]:
                cfg.expr = _translate_filter(search_kwargs["expr"])
            if "vector_weight" in search_kwargs:
                cfg.vector_weight = float(search_kwargs["vector_weight"])
            if "use_rrf" in search_kwargs:
                cfg.use_rrf = bool(search_kwargs["use_rrf"])
        return LanceDBRetriever(table=self._table, embeddings=self._embeddings, search_cfg=cfg)

    # ------------------------------------------------------------------
    # Core query path
    # ------------------------------------------------------------------

    def invoke(self, query: str) -> List[Document]:
        query = (query or "").strip()
        if not query:
            return []

        qvec = self._embeddings.embed_query(query)

        # Pull candidates from each side separately, then fuse with RRF.
        # We fetch 3x the requested k on each side so the fused list has
        # enough redundancy to produce k strong final results.
        candidate_k = max(self._cfg.k * 3, 20)

        vec_hits = self._vector_search(qvec, candidate_k)
        bm25_hits = self._fts_search(query, candidate_k)

        if self._cfg.use_rrf:
            fused = _rrf_fuse([vec_hits, bm25_hits], k=_RRF_K)
        else:
            fused = _linear_fuse(vec_hits, bm25_hits, vector_weight=self._cfg.vector_weight)

        return _rows_to_documents(fused[: self._cfg.k])

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _vector_search(self, qvec: List[float], limit: int) -> List[Dict[str, Any]]:
        try:
            q = self._table.search(qvec, vector_column_name=_VECTOR_COLUMN).limit(limit)
            if self._cfg.expr:
                q = q.where(self._cfg.expr, prefilter=True)
            return q.to_list()
        except Exception:
            return []

    def _fts_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        try:
            q = self._table.search(query, query_type="fts").limit(limit)
            if self._cfg.expr:
                q = q.where(self._cfg.expr, prefilter=True)
            return q.to_list()
        except Exception:
            # FTS index may not exist yet (e.g. during a brand new ingest).
            return []


# ---------------------------------------------------------------------------
# Public vectorstore adapter (mirrors MilvusClientVectorStoreAdapter)
# ---------------------------------------------------------------------------


class LanceDBVectorStoreAdapter:
    """Exposes ``.as_retriever(search_kwargs=...)`` so protocol_retrieval works unchanged."""

    def __init__(self, *, table: Any, embeddings: Any) -> None:
        self._table = table
        self._embeddings = embeddings

    def as_retriever(self, search_kwargs: Optional[Dict[str, Any]] = None) -> LanceDBRetriever:
        base = LanceDBRetriever(table=self._table, embeddings=self._embeddings)
        return base.with_search_kwargs(search_kwargs)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_lancedb_vectorstore(
    _embeddings: Any,
    *,
    db_path: Optional[str] = None,
    table_name: Optional[str] = None,
) -> Optional[LanceDBVectorStoreAdapter]:
    """Open an existing LanceDB table. Returns None if the table is missing."""
    try:
        import lancedb  # noqa: F401
    except ImportError as e:
        raise RuntimeError(
            "lancedb is not installed. Run: pip install lancedb tantivy"
        ) from e

    import lancedb

    path = _resolve_db_path(db_path)
    name = _resolve_table_name(table_name)

    db = lancedb.connect(path)
    if name not in _list_tables(db):
        return None
    table = db.open_table(name)
    return LanceDBVectorStoreAdapter(table=table, embeddings=_embeddings)


# ---------------------------------------------------------------------------
# Utility: filter translation, fusion, row conversion
# ---------------------------------------------------------------------------


_MILVUS_EQ_RE = re.compile(r'(\w+)\s*==\s*"([^"]+)"')


def _translate_filter(expr: str) -> str:
    """Translate a small subset of Milvus expr syntax into LanceDB SQL WHERE.

    Only handles ``field == "value"`` because that's what protocol_retrieval
    currently emits. Anything more exotic should be authored in SQL directly.
    """
    def sub(match: re.Match) -> str:
        field, value = match.group(1), match.group(2)
        return f"{field} = '{value}'"

    return _MILVUS_EQ_RE.sub(sub, expr)


def _row_key(row: Dict[str, Any]) -> str:
    """Stable identity for a retrieved row so RRF can dedupe across searches."""
    rid = row.get("id")
    if rid:
        return str(rid)
    # Fall back to a prefix of text + source; protocol chunks are long
    # enough that 200 chars + filename is effectively unique.
    text = (row.get(_FTS_COLUMN) or "")[:200]
    src = row.get("protocol_relpath") or row.get("source") or ""
    return f"{src}::{text}"


def _rrf_fuse(ranked_lists: Iterable[List[Dict[str, Any]]], *, k: int = _RRF_K) -> List[Dict[str, Any]]:
    """Reciprocal Rank Fusion: score(d) = sum 1/(k + rank_i(d)).

    The classic Cormack/Lynam/Büttcher 2009 formulation. k=60 by default.
    """
    scores: Dict[str, float] = {}
    payload: Dict[str, Dict[str, Any]] = {}
    for ranked in ranked_lists:
        for rank, row in enumerate(ranked):
            key = _row_key(row)
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
            # Keep the first payload we see; LanceDB returns the same fields
            # regardless of which index served the hit.
            payload.setdefault(key, row)
    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return [dict(payload[key], _rrf_score=score) for key, score in ordered]


def _linear_fuse(
    vec_hits: List[Dict[str, Any]],
    bm25_hits: List[Dict[str, Any]],
    *,
    vector_weight: float,
) -> List[Dict[str, Any]]:
    """Fallback: normalize + weighted sum. Used only if use_rrf=False."""
    w_vec = max(0.0, min(1.0, vector_weight))
    w_bm = 1.0 - w_vec
    scored: Dict[str, float] = {}
    payload: Dict[str, Dict[str, Any]] = {}

    def add(rows: List[Dict[str, Any]], weight: float, score_field_candidates: List[str]) -> None:
        if not rows:
            return
        raw = []
        for r in rows:
            s = 0.0
            for f in score_field_candidates:
                if f in r and r[f] is not None:
                    s = float(r[f])
                    break
            raw.append(s)
        # Min-max normalize so vector distance and BM25 score live on the
        # same 0..1 scale before the weighted sum.
        if raw:
            lo, hi = min(raw), max(raw)
            span = (hi - lo) or 1.0
            for row, s in zip(rows, raw):
                norm = (s - lo) / span
                # LanceDB returns smaller distance = better for vector search,
                # so flip when the field is _distance.
                if "_distance" in row:
                    norm = 1.0 - norm
                key = _row_key(row)
                scored[key] = scored.get(key, 0.0) + weight * norm
                payload.setdefault(key, row)

    add(vec_hits, w_vec, ["_distance", "_score"])
    add(bm25_hits, w_bm, ["_score", "score"])

    ordered = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)
    return [dict(payload[key], _hybrid_score=score) for key, score in ordered]


def _rows_to_documents(rows: List[Dict[str, Any]]) -> List[Document]:
    docs: List[Document] = []
    for row in rows:
        text = row.get(_FTS_COLUMN) or ""
        if not text:
            continue
        meta = {k: v for k, v in row.items() if k not in (_FTS_COLUMN, _VECTOR_COLUMN)}
        # Drop the raw vector and LanceDB internals from metadata surface.
        meta.pop("_rowid", None)
        docs.append(Document(page_content=text, metadata=meta))
    return docs
