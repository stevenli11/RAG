"""Embedding backend factory.

Two backends are supported:

- ``dashscope`` (default for parity with the deployed RAG): calls Alibaba's
  configured embedding API. Costs tokens from your DashScope quota.
- ``local`` (default): runs a small sentence-transformers model on-device (BGE by default).
  Free, offline, CPU-friendly. Best when you're rate-limited on DashScope or
  developing locally.

The returned object is langchain-compatible (has ``embed_documents`` and
``embed_query``), so LanceDBRetriever / ProtocolRetrievalSkill don't care
which backend produced it — the only hard rule is **ingest and query must
use the same backend and model**, otherwise the vectors are not comparable.
"""

from __future__ import annotations

from http import HTTPStatus
import os
from typing import Any, List, Optional

from langchain_core.embeddings import Embeddings


_MULTIMODAL_MODEL_MARKERS = (
    "embedding-vision",
    "vl-embedding",
    "multimodal-embedding",
)


def _is_multimodal_embedding_model(model_name: str) -> bool:
    return any(marker in model_name for marker in _MULTIMODAL_MODEL_MARKERS)


class DashScopeMultiModalEmbeddings(Embeddings):
    """LangChain-compatible wrapper for DashScope MultiModalEmbedding.

    LangChain's built-in DashScopeEmbeddings always calls dashscope.TextEmbedding.
    Newer models such as tongyi-embedding-vision-plus-2026-03-06 require
    dashscope.MultiModalEmbedding, even for text-only inputs.
    """

    def __init__(
        self,
        *,
        model: str,
        dashscope_api_key: str,
        dimension: Optional[int] = None,
        batch_size: int = 20,
    ) -> None:
        self.model = model
        self.dashscope_api_key = dashscope_api_key
        self.dimension = dimension
        self.batch_size = batch_size

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for start in range(0, len(texts), self.batch_size):
            vectors.extend(self._embed_batch(texts[start : start + self.batch_size]))
        return vectors

    def embed_query(self, text: str) -> List[float]:
        return self._embed_batch([text])[0]

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        import dashscope

        kwargs: dict[str, Any] = {
            "api_key": self.dashscope_api_key,
            "model": self.model,
            "input": [{"text": text} for text in texts],
        }
        if self.dimension:
            kwargs["dimension"] = self.dimension

        resp = dashscope.MultiModalEmbedding.call(**kwargs)
        if resp.status_code != HTTPStatus.OK:
            raise ValueError(
                f"status_code: {resp.status_code}\n"
                f"code: {getattr(resp, 'code', '')}\n"
                f"message: {getattr(resp, 'message', '')}"
            )

        embeddings = resp.output.get("embeddings", [])
        embeddings = sorted(embeddings, key=lambda item: item.get("index", 0))
        return [item["embedding"] for item in embeddings]


def get_embeddings(backend: Optional[str] = None, model: Optional[str] = None) -> Any:
    """Return a langchain Embeddings object for the selected backend.

    Resolution order:
      1. explicit ``backend`` / ``model`` arguments
      2. env vars ``EMBEDDING_BACKEND`` / ``EMBEDDING_MODEL``
      3. defaults (``local`` + ``BAAI/bge-small-en-v1.5``)
    """
    from dotenv import load_dotenv
    load_dotenv()

    backend = (backend or os.getenv("EMBEDDING_BACKEND", "local")).lower().strip()

    if backend == "dashscope":
        api_key = os.getenv("DASHSCOPE_API_KEY", "").strip().strip('"').strip("'")
        if not api_key:
            raise SystemExit(
                "DASHSCOPE_API_KEY is not set. Either fill it in .env or set "
                "EMBEDDING_BACKEND=local to use a free on-device model."
            )
        model_name = model or os.getenv("EMBEDDING_MODEL", "tongyi-embedding-vision-plus-2026-03-06")
        if _is_multimodal_embedding_model(model_name):
            dimension = os.getenv("EMBEDDING_DIMENSION", "").strip()
            return DashScopeMultiModalEmbeddings(
                model=model_name,
                dashscope_api_key=api_key,
                dimension=int(dimension) if dimension else None,
            )
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
        local_only = os.getenv("EMBEDDING_LOCAL_FILES_ONLY", "").lower() in {"1", "true", "yes"}
        local_only = local_only or os.getenv("HF_HUB_OFFLINE", "").lower() in {"1", "true", "yes"}
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"local_files_only": local_only},
            encode_kwargs={"normalize_embeddings": True},
        )

    raise SystemExit(f"Unknown EMBEDDING_BACKEND={backend!r} (expected dashscope|local)")
