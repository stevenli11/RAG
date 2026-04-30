import logging
from langchain_milvus import Milvus
from langchain_core.documents import Document
from pymilvus import MilvusClient
import time
from typing import Any, Dict, List, Optional
from rag_app.utils.text_cleaning import clean_collection_name


logger = logging.getLogger(__name__)


class _MilvusClientRetriever:
    """Fallback retriever adapter when langchain_milvus alias handling fails."""

    def __init__(
        self,
        *,
        client: MilvusClient,
        embeddings: Any,
        collection_name: str,
        vector_field: str = "vector",
        text_field: str = "text",
    ) -> None:
        self.client = client
        self.embeddings = embeddings
        self.collection_name = collection_name
        self.vector_field = vector_field
        self.text_field = text_field
        self._search_kwargs: Dict[str, Any] = {"k": 8}

    def with_search_kwargs(self, search_kwargs: Optional[Dict[str, Any]] = None) -> "_MilvusClientRetriever":
        cloned = _MilvusClientRetriever(
            client=self.client,
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            vector_field=self.vector_field,
            text_field=self.text_field,
        )
        if search_kwargs:
            cloned._search_kwargs = dict(search_kwargs)
        return cloned

    def invoke(self, query: str) -> List[Document]:
        k = int(self._search_kwargs.get("k", 8))
        expr = self._search_kwargs.get("expr")
        qvec = self.embeddings.embed_query(query)
        output_fields = ["text", "source", "protocol_file", "protocol_relpath", "source_type"]
        try:
            result = self.client.search(
                collection_name=self.collection_name,
                data=[qvec],
                anns_field=self.vector_field,
                limit=k,
                output_fields=output_fields,
                filter=expr,
            )
        except TypeError:
            result = self.client.search(
                collection_name=self.collection_name,
                data=[qvec],
                anns_field=self.vector_field,
                limit=k,
                output_fields=output_fields,
                expr=expr,
            )
        hits = result[0] if result else []
        docs: List[Document] = []
        for hit in hits:
            entity = hit.get("entity", {}) if isinstance(hit, dict) else (getattr(hit, "entity", {}) or {})
            score = hit.get("distance", hit.get("score")) if isinstance(hit, dict) else getattr(hit, "distance", None)
            page_content = entity.get(self.text_field) or ""
            if not page_content:
                continue
            metadata = {k: v for k, v in entity.items() if k != self.text_field}
            if score is not None:
                metadata["score"] = float(score)
            docs.append(Document(page_content=page_content, metadata=metadata))
        return docs


class MilvusClientVectorStoreAdapter:
    """VectorStore-like adapter exposing as_retriever(search_kwargs)."""

    def __init__(self, *, client: MilvusClient, embeddings: Any, collection_name: str) -> None:
        self.client = client
        self.embeddings = embeddings
        self.collection_name = collection_name

    def as_retriever(self, search_kwargs: Optional[Dict[str, Any]] = None) -> _MilvusClientRetriever:
        base = _MilvusClientRetriever(
            client=self.client,
            embeddings=self.embeddings,
            collection_name=self.collection_name,
        )
        return base.with_search_kwargs(search_kwargs)


def load_vectorstore(config, _embeddings, collection_name=None):
    """Load a vector store based on ``config['vector_backend']``.

    - ``lancedb`` (default here in RAG_local): embedded local store with
      hybrid BM25+vector search. Ingest via
      ``scripts/ingest_protocols_lancedb.py`` first.
    - ``milvus``: legacy Zilliz cloud path, kept intact below.
    """
    backend = (config.get("vector_backend") or "lancedb").lower()
    if backend == "lancedb":
        from rag_app.data.lancedb_backend import load_lancedb_vectorstore
        store = load_lancedb_vectorstore(
            _embeddings,
            db_path=config.get("lancedb_path"),
            table_name=config.get("lancedb_table"),
        )
        if store is None:
            logger.warning(
                "LanceDB table not found. Run `python scripts/ingest_protocols_lancedb.py` to build it."
            )
        return store

    # Clean collection name to ensure it meets Milvus requirements
    if not collection_name:
        collection_name = config.get("milvus_collection", "company_milvus")
    collection_name = clean_collection_name(collection_name)
    uri = config["milvus_uri"]
    user = config.get("milvus_user", "")
    password = config.get("milvus_password", "")
    token = config.get("milvus_token", "") or (f"{user}:{password}" if user and password else "")
    if not token:
        logger.error(
            "Milvus auth is empty. Please set MILVUS_TOKEN (recommended) or MILVUS_USER/MILVUS_PASSWORD."
        )
        return None

    # Docs-aligned LangChain Milvus usage for Zilliz Cloud:
    # pass uri + token via connection_args and let langchain_milvus manage connection alias.
    connection_args = {"uri": uri, "token": token, "secure": True}
    last_error = None
    for _ in range(3):
        try:
            vectorstore = Milvus(
                embedding_function=_embeddings,
                collection_name=collection_name,
                connection_args=connection_args,
            )
            return vectorstore
        except Exception as e:
            # Known intermittent issue on some langchain_milvus/pymilvus combinations:
            # alias is not registered and raises ConnectionNotExistException.
            if "ConnectionNotExistException" in str(e):
                try:
                    client = MilvusClient(uri=uri, token=token)
                    existing = set(client.list_collections() or [])
                    if collection_name not in existing:
                        logger.warning(
                            "Milvus is connected, but collection `%s` does not exist yet. Build the index first.",
                            collection_name,
                        )
                        return None
                    return MilvusClientVectorStoreAdapter(
                        client=client,
                        embeddings=_embeddings,
                        collection_name=collection_name,
                    )
                except Exception as inner:
                    last_error = inner
                    time.sleep(1.2)
                    continue
            last_error = e
            time.sleep(1.2)
            continue

    logger.error("Failed to load existing collection: %s", last_error)
    logger.info(
        "Tip: use the Zilliz Python connection endpoint, set MILVUS_TOKEN, and verify MILVUS_COLLECTION."
    )
    return None
