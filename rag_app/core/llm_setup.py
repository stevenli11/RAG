import dashscope
from langchain_openai import ChatOpenAI

from rag_app.core.embeddings import get_embeddings

def initialize_llm(config):
    """Initialize LLMs (cached)."""
    dashscope.api_key = config["dashscope_key"]
    
    # Large model for answer generation (with streaming enabled).
    # qwen3.6-plus defaults to "thinking-mode" — it generates internal
    # reasoning_content tokens BEFORE the first visible content chunk.
    # We KEEP thinking on for higher answer quality, especially on the
    # ObjectiveAudit "challenge user data" reasoning and on compound
    # medical questions. The frontend SSE watchdog has been extended to
    # accommodate the extra TTFT.
    graph_llm = ChatOpenAI(
        temperature=0,
        model_name="qwen3.6-plus",
        api_key=config["dashscope_key"],
        base_url=config["dashscope_base_url"],
        streaming=True,
    )

    # Small model for query rewriting, classification, audit, citation
    # verification, follow-up generation, history compression.
    # qwen3.5-flash expired in this account; qwen3.6-flash is the current
    # low-latency Qwen route.
    #
    # Thinking-mode is DISABLED for small_llm: these tasks are
    # constraint-following (emit valid JSON, classify into known buckets)
    # rather than open-ended reasoning, so internal thinking adds 5-10s
    # per call without measurable quality gain. We keep thinking ON only
    # on graph_llm (answer generation) where the extra reasoning matters.
    small_llm = ChatOpenAI(
        temperature=0,
        model_name="qwen3.6-flash",
        api_key=config["dashscope_key"],
        base_url=config["dashscope_base_url"],
        extra_body={"enable_thinking": False},
    )
    
    return graph_llm, small_llm

def initialize_embeddings(config):
    """Initialize embeddings (cached)."""
    dashscope.api_key = config["dashscope_key"]

    return get_embeddings(
        backend=config.get("embedding_backend") or "local",
        model=config.get("embedding_model") or "BAAI/bge-small-en-v1.5",
    )
