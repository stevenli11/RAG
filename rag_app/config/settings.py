import os
from dotenv import load_dotenv

def get_config(
    user_milvus_uri=None,
    user_milvus_user=None,
    user_milvus_password=None,
    user_milvus_token=None,
    user_milvus_collection=None,
    user_rerank_model=None,
):
    """Get config from app secrets/env and optional user Milvus override.

    Security policy:
    - LLM/API keys are server-managed only (NOT user-editable in UI).
    - Users may still provide their own Milvus endpoint for private indexing.
    """
    dashscope_key = ""
    dashscope_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    milvus_uri = user_milvus_uri or ""
    milvus_user = user_milvus_user or ""
    milvus_password = user_milvus_password or ""
    milvus_token = user_milvus_token or ""
    milvus_collection = user_milvus_collection or ""
    rerank_model = user_rerank_model or ""
    pubmed_api_key = ""
    vector_backend = ""
    lancedb_path = ""
    lancedb_table = ""
    embedding_backend = ""
    embedding_model = ""
    rerank_backend = ""
    local_rerank_model = ""
    
    # Read configuration from environment variables.
    if not dashscope_key:
        load_dotenv()
        dashscope_key = os.getenv("DASHSCOPE_API_KEY", "").strip().strip('"').strip("'")
        dashscope_base_url = os.getenv("DASHSCOPE_API_BASE", dashscope_base_url)
    
    if not milvus_uri:
        load_dotenv()
        milvus_uri = os.getenv("MILVUS_URI", "")
        milvus_user = os.getenv("MILVUS_USER", "")
        milvus_password = os.getenv("MILVUS_PASSWORD", "")
    if not milvus_token:
        load_dotenv()
        milvus_token = os.getenv("MILVUS_TOKEN", "")
    if not milvus_collection:
        load_dotenv()
        milvus_collection = os.getenv("MILVUS_COLLECTION", "")
    if not rerank_model:
        load_dotenv()
        rerank_model = os.getenv("RERANK_MODEL", "")
    
    if not pubmed_api_key:
        load_dotenv()
        pubmed_api_key = os.getenv("PUBMED_API_KEY", "").strip().strip('"').strip("'")

    if not vector_backend:
        load_dotenv()
        vector_backend = os.getenv("VECTOR_BACKEND", "")
    if not lancedb_path:
        load_dotenv()
        lancedb_path = os.getenv("LANCEDB_PATH", "")
    if not lancedb_table:
        load_dotenv()
        lancedb_table = os.getenv("LANCEDB_TABLE", "")
    if not embedding_backend:
        load_dotenv()
        embedding_backend = os.getenv("EMBEDDING_BACKEND", "")
    if not embedding_model:
        load_dotenv()
        embedding_model = os.getenv("EMBEDDING_MODEL", "")
    if not rerank_backend:
        load_dotenv()
        rerank_backend = os.getenv("RERANK_BACKEND", "")
    if not local_rerank_model:
        load_dotenv()
        local_rerank_model = os.getenv("LOCAL_RERANK_MODEL", "")

    return {
        "dashscope_key": dashscope_key.strip().strip('"').strip("'") if dashscope_key else "",
        "dashscope_base_url": dashscope_base_url,
        "milvus_uri": milvus_uri,
        "milvus_user": milvus_user,
        "milvus_password": milvus_password,
        "milvus_token": (milvus_token or "").strip(),
        "milvus_collection": (milvus_collection or "company_milvus"),
        # Set RERANK_MODEL=none/off/disabled to skip DashScope rerank entirely.
        # Useful when the provider retires or quota-blocks rerank models; the
        # pipeline falls back to LanceDB hybrid retrieval + keyword scoring.
        "rerank_model": (rerank_model or "none"),
        "rerank_backend": (rerank_backend or "none").strip().lower(),
        "local_rerank_model": (local_rerank_model or "BAAI/bge-reranker-base").strip(),
        "embedding_backend": (embedding_backend or "local").strip().lower(),
        "embedding_model": (embedding_model or "BAAI/bge-small-en-v1.5").strip(),
        "pubmed_api_key": pubmed_api_key if pubmed_api_key else "",
        # "lancedb" (default here in RAG_local, hybrid BM25+vec) | "milvus" (legacy cloud)
        "vector_backend": (vector_backend or "lancedb").strip().lower(),
        "lancedb_path": (lancedb_path or "./data/lancedb").strip(),
        "lancedb_table": (lancedb_table or "protocols").strip(),
    }
