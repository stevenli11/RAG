"""Local cross-encoder rerank helpers.

Used when provider-hosted rerank models are expired or quota-blocked. The
helper is intentionally small: callers pass plain texts and get ranked indices
back. If the local model is unavailable, callers fall back to their existing
keyword / retrieval order.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Iterable, List, Tuple


_DISABLED = {"", "none", "off", "disabled", "false", "0"}
DEFAULT_LOCAL_RERANK_MODEL = "BAAI/bge-reranker-base"


def disabled_rerank_value(value: str | None) -> bool:
    return (value or "").strip().lower() in _DISABLED


def rerank_backend(config: dict) -> str:
    raw = os.getenv("RERANK_BACKEND") or str(config.get("rerank_backend") or "")
    return (raw or "none").strip().lower()


def local_rerank_model(config: dict) -> str:
    raw = os.getenv("LOCAL_RERANK_MODEL") or str(config.get("local_rerank_model") or "")
    # If RERANK_BACKEND=local and RERANK_MODEL is not a disabled sentinel, let
    # RERANK_MODEL also name the local cross-encoder for convenience.
    if not raw:
        candidate = str(config.get("rerank_model") or "")
        if not disabled_rerank_value(candidate):
            raw = candidate
    return (raw or DEFAULT_LOCAL_RERANK_MODEL).strip()


@lru_cache(maxsize=2)
def _load_cross_encoder(model_name: str):
    from sentence_transformers import CrossEncoder

    return CrossEncoder(model_name)


def local_rerank_texts(
    *,
    query: str,
    texts: Iterable[str],
    top_n: int,
    model_name: str = DEFAULT_LOCAL_RERANK_MODEL,
) -> List[Tuple[int, float]]:
    """Return ``[(original_index, score), ...]`` sorted best-first."""
    text_list = [str(t or "") for t in texts]
    if not text_list or top_n <= 0:
        return []

    model = _load_cross_encoder(model_name)
    pairs = [(query, text) for text in text_list]
    scores = model.predict(pairs)
    ranked = sorted(
        ((idx, float(score)) for idx, score in enumerate(scores)),
        key=lambda item: item[1],
        reverse=True,
    )
    return ranked[: min(top_n, len(ranked))]
