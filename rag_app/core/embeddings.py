"""Embedding backend factory.

Two backends are supported:

- ``dashscope`` (default for parity with the original RAG): calls Alibaba's
  ``text-embedding-v4`` API. Costs tokens from your DashScope quota.
- ``local``: runs a small sentence-transformers model on-device (BGE by default).
  Free, offline, CPU-friendly. Best when you're rate-limited on DashScope or
  developing locally.

The returned object is langchain-compatible (has ``embed_documents`` and
``embed_query``), so LanceDBRetriever / ProtocolRetrievalSkill don't care
which backend produced it — the only hard rule is **ingest and query must
use the same backend and model**, otherwise the vectors are not comparable.
"""

from __future__ import annotations

import os
from typing import Any, Optional


def get_embeddings(backend: Optional[str] = None, model: Optional[str] = None) -> Any:
    """Return a langchain Embeddings object for the selected backend.

    Resolution order:
      1. explicit ``backend`` / ``model`` arguments
      2. env vars ``EMBEDDING_BACKEND`` / ``EMBEDDING_MODEL``
      3. defaults (``dashscope`` + ``text-embedding-v4``)
    """
    from dotenv import load_dotenv
    load_dotenv()

    backend = (backend or os.getenv("EMBEDDING_BACKEND", "dashscope")).lower().strip()

    if backend == "dashscope":
        api_key = os.getenv("DASHSCOPE_API_KEY", "").strip().strip('"').strip("'")
        if not api_key:
            raise SystemExit(
                "DASHSCOPE_API_KEY is not set. Either fill it in .env or set "
                "EMBEDDING_BACKEND=local to use a free on-device model."
            )
        model_name = model or os.getenv("EMBEDDING_MODEL", "text-embedding-v4")
        from langchain_community.embeddings import DashScopeEmbeddings
        return DashScopeEmbeddings(model=model_name, dashscope_api_key=api_key)

    if backend == "local":
        # BGE-small is 33M params / ~130 MB / 384 dims. Strong MTEB scores,
        # CPU-fast, no API calls. Swap to ``bge-base`` or ``bge-m3`` later if
        # retrieval quality warrants the extra memory.
        model_name = model or os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
        # Prefer the new ``langchain-huggingface`` package; fall back to the
        # community shim so older envs keep working. The community version is
        # deprecated and will be removed in langchain 0.3.x.
        try:
            from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore
        except ImportError:
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore
            except ImportError as e:
                raise SystemExit(
                    "Local embeddings need sentence-transformers + langchain-huggingface. Run:\n"
                    "    pip install sentence-transformers langchain-huggingface"
                ) from e
        return HuggingFaceEmbeddings(
            model_name=model_name,
            encode_kwargs={"normalize_embeddings": True},
        )

    raise SystemExit(f"Unknown EMBEDDING_BACKEND={backend!r} (expected dashscope|local)")
