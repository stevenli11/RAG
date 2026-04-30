import dashscope
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings

def initialize_llm(config):
    """Initialize LLMs (cached)."""
    dashscope.api_key = config["dashscope_key"]
    
    # Large model for answer generation (with streaming enabled).
    # Switched qwen-plus → qwen-max (qwen-plus quota exhausted; qwen3.6-plus
    # was slower due to thinking-mode, so we prefer qwen-max for TTFT).
    graph_llm = ChatOpenAI(
        temperature=0,
        model_name="qwen-max",
        api_key=config["dashscope_key"],
        base_url=config["dashscope_base_url"],
        streaming=True  # Enable streaming for better UX
    )
    
    # Small model for query rewriting and classification (cost-effective)
    small_llm = ChatOpenAI(
        temperature=0,
        model_name="qwen-flash",
        api_key=config["dashscope_key"],
        base_url=config["dashscope_base_url"]
    )
    
    return graph_llm, small_llm

def initialize_embeddings(config):
    """Initialize embeddings (cached)."""
    dashscope.api_key = config["dashscope_key"]
    
    base_embeddings = DashScopeEmbeddings(
        model="text-embedding-v4",
        dashscope_api_key=config["dashscope_key"]
    )
    
    return base_embeddings
