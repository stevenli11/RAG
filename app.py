"""
Streamlit RAG Agent Application
RAG QA system built with LangChain, DashScope LLM and Milvus vector database.
"""

import os
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_milvus import Milvus
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import dashscope
from http import HTTPStatus
from typing import List

# Page config
st.set_page_config(
    page_title="RAG QA Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 辅助函数 ==========

def clean_text(text):
    """Clean text and remove characters that may cause encoding issues."""
    if not text:
        return ""
    # 移除控制字符（除了换行、制表符和回车）
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    # 移除零宽字符
    text = re.sub(r'[\u200b-\u200f\u202a-\u202e\u2060-\u206f]', '', text)
    # 确保文本可以正确编码为 UTF-8
    try:
        text.encode('utf-8')
    except UnicodeEncodeError:
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
    return text


def clean_metadata_key(key):
    """Clean metadata field names to satisfy Milvus naming rules (only letters, numbers and underscores)."""
    if not key:
        return "unknown"
    # 将不符合规范的字符替换为下划线
    # Milvus 字段名只能包含：数字、字母、下划线
    cleaned_key = re.sub(r'[^a-zA-Z0-9_]', '_', str(key))
    # 确保字段名不为空，且不以数字开头（如果可能的话）
    if not cleaned_key or cleaned_key[0].isdigit():
        cleaned_key = "field_" + cleaned_key
    return cleaned_key


def get_config(user_dashscope_key=None, user_milvus_uri=None, user_milvus_user=None, user_milvus_password=None):
    """Get config from user input, Streamlit secrets or environment variables."""
    # 优先使用用户输入的配置
    dashscope_key = user_dashscope_key or ""
    dashscope_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    milvus_uri = user_milvus_uri or ""
    milvus_user = user_milvus_user or ""
    milvus_password = user_milvus_password or ""
    
    # 如果用户没有输入，尝试从 Streamlit secrets 读取
    if not dashscope_key or not milvus_uri:
        try:
            secrets = st.secrets
            
            # DashScope API Key（如果用户未输入）
            if not dashscope_key:
                dashscope_key = secrets.get("DASHSCOPE_API_KEY", "")
                dashscope_base_url = secrets.get("DASHSCOPE_API_BASE", dashscope_base_url)
            
            # Milvus 配置（如果用户未输入）
            if not milvus_uri:
                milvus_uri = secrets.get("MILVUS_URI", "")
                milvus_user = secrets.get("MILVUS_USER", "")
                milvus_password = secrets.get("MILVUS_PASSWORD", "")
        except (AttributeError, FileNotFoundError, KeyError):
            # Streamlit secrets 不可用，使用环境变量
            pass
    
    # 如果还是没有，回退到环境变量
    if not dashscope_key:
        load_dotenv()
        dashscope_key = os.getenv("DASHSCOPE_API_KEY", "").strip().strip('"').strip("'")
        dashscope_base_url = os.getenv("DASHSCOPE_API_BASE", dashscope_base_url)
    
    if not milvus_uri:
        load_dotenv()
        milvus_uri = os.getenv("MILVUS_URI", "")
        milvus_user = os.getenv("MILVUS_USER", "")
        milvus_password = os.getenv("MILVUS_PASSWORD", "")
    
    return {
        "dashscope_key": dashscope_key.strip().strip('"').strip("'") if dashscope_key else "",
        "dashscope_base_url": dashscope_base_url,
        "milvus_uri": milvus_uri,
        "milvus_user": milvus_user,
        "milvus_password": milvus_password,
    }


@st.cache_resource
def initialize_llm(config):
    """Initialize LLMs (cached)."""
    dashscope.api_key = config["dashscope_key"]
    
    graph_llm = ChatOpenAI(
        temperature=0,
        model_name="qwen-plus-2025-12-01",
        api_key=config["dashscope_key"],
        base_url=config["dashscope_base_url"]
    )
    
    llm = ChatOpenAI(
        temperature=0,
        model_name="qwen-plus",
        api_key=config["dashscope_key"],
        base_url=config["dashscope_base_url"]
    )
    
    return graph_llm, llm


@st.cache_resource
def initialize_embeddings(config):
    """Initialize embeddings (cached)."""
    dashscope.api_key = config["dashscope_key"]
    
    base_embeddings = DashScopeEmbeddings(
        model="text-embedding-v4",
        dashscope_api_key=config["dashscope_key"]
    )
    
    return base_embeddings


@st.cache_resource
def load_vectorstore(config, _embeddings, collection_name="company_milvus"):
    """Load or create Milvus vector store (cached)."""
    connection_args = {
        "uri": config["milvus_uri"],
        "user": config["milvus_user"],
        "password": config["milvus_password"],
    }
    
    try:
        # Try to load existing collection
        vectorstore = Milvus(
            embedding_function=_embeddings,
            collection_name=collection_name,
            connection_args=connection_args
        )
        # Test that retrieval works
        test_retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
        test_docs = test_retriever.invoke("test")
        return vectorstore
    except Exception as e:
        st.error(f"⚠️ Failed to load existing collection: {e}")
        st.info("💡 If this is your first time, please upload a document and build the vector index first.")
        return None


def process_uploaded_file(uploaded_file, embeddings, config, collection_name="company_milvus"):
    """Process uploaded file and build vector index."""
    # Save temporary file
    temp_file_path = f"/tmp/{uploaded_file.name}"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        # Load documents
        if uploaded_file.name.endswith('.pdf'):
            loader = PyPDFLoader(temp_file_path)
            documents = loader.load()
        else:
            loader = TextLoader(temp_file_path, encoding='utf-8')
            documents = loader.load()
        
        # Clean documents
        for doc in documents:
            doc.page_content = clean_text(doc.page_content)
            if doc.metadata:
                cleaned_metadata = {}
                for key, value in doc.metadata.items():
                    # Clean field names to satisfy Milvus naming rules
                    cleaned_key = clean_metadata_key(key)
                    if isinstance(value, str):
                        cleaned_metadata[cleaned_key] = clean_text(value)
                    else:
                        cleaned_metadata[cleaned_key] = value
                doc.metadata = cleaned_metadata
        
        # Text splitting
        chunk_size = 250
        chunk_overlap = 30
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        splits = text_splitter.split_documents(documents)
        
        # Clean again
        cleaned_splits = []
        for doc in splits:
            cleaned_content = clean_text(doc.page_content)
            if cleaned_content.strip():
                doc.page_content = cleaned_content
                # Clean metadata field names again (split docs may keep original metadata)
                if doc.metadata:
                    cleaned_metadata = {}
                    for key, value in doc.metadata.items():
                        cleaned_key = clean_metadata_key(key)
                        if isinstance(value, str):
                            cleaned_metadata[cleaned_key] = clean_text(value)
                        else:
                            cleaned_metadata[cleaned_key] = value
                    doc.metadata = cleaned_metadata
                cleaned_splits.append(doc)
        
        splits = cleaned_splits
        
        # Build vector index
        connection_args = {
            "uri": config["milvus_uri"],
            "user": config["milvus_user"],
            "password": config["milvus_password"],
        }
        
        vectorstore = Milvus.from_documents(
            documents=splits,
            collection_name=collection_name,
            embedding=embeddings,
            connection_args=connection_args
        )
        
        # Remove temporary file
        os.remove(temp_file_path)
        
        return vectorstore, len(splits)
        
    except Exception as e:
        # Remove temporary file on error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise e


def create_rag_chain(graph_llm):
    """Create RAG chain for answering questions."""
    prompt = PromptTemplate(
        template="""You are an immunology experiment-planning assistant.
Design an executable experimental plan using ONLY the provided context. Do NOT invent parameters (e.g., concentrations, incubation times, catalog numbers, instrument models) unless explicitly stated in the context.

Rules:
1) If the context has relevant info, propose a minimal, actionable plan tailored to the goal.
2) If critical details are missing, ask up to 3 clarifying questions (only the most critical).
3) Keep the response concise, but prioritize actionability over being short.

Question: {question}
Context: {context}

Answer in this format:
- Goal:
- Hypothesis:
- Minimal plan (3-7 steps):
- Controls:
- Readouts:
- Missing critical info (if any):
- Clarifying questions (0-3):""",
        input_variables=["question", "context"],
    )
    
    return prompt | graph_llm | StrOutputParser()


# ========== Main app ==========

def main():
    st.title("🤖 RAG QA Assistant")
    st.markdown("Retrieval-augmented generation system powered by LangChain + DashScope + Milvus.")
    
    # Sidebar: configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Initialize session_state
        if "dashscope_key" not in st.session_state:
            st.session_state.dashscope_key = ""
        if "milvus_uri" not in st.session_state:
            st.session_state.milvus_uri = ""
        if "milvus_user" not in st.session_state:
            st.session_state.milvus_user = ""
        if "milvus_password" not in st.session_state:
            st.session_state.milvus_password = ""
        
        # DashScope API Key input
        st.markdown("### 🔑 DashScope API Key")
        dashscope_key_input = st.text_input(
            "DashScope API Key",
            value=st.session_state.dashscope_key,
            type="password",
            help="Enter your DashScope API Key from Alibaba Cloud DashScope.",
            key="dashscope_key_input"
        )
        if dashscope_key_input:
            st.session_state.dashscope_key = dashscope_key_input
            st.caption("💡 [Get a DashScope API Key](https://dashscope.console.aliyun.com/)")
        else:
            st.caption("💡 Please enter your DashScope API Key to use this app.")
        
        st.markdown("---")
        
        # Milvus configuration input
        st.markdown("### 🗄️ Milvus configuration")
        milvus_uri_input = st.text_input(
            "Milvus URI",
            value=st.session_state.milvus_uri,
            type="default",
            help="Milvus connection URI.",
            key="milvus_uri_input"
        )
        if milvus_uri_input:
            st.session_state.milvus_uri = milvus_uri_input
        
        milvus_user_input = st.text_input(
            "Milvus User",
            value=st.session_state.milvus_user,
            type="default",
            help="Milvus username.",
            key="milvus_user_input"
        )
        if milvus_user_input:
            st.session_state.milvus_user = milvus_user_input
        
        milvus_password_input = st.text_input(
            "Milvus Password",
            value=st.session_state.milvus_password,
            type="password",
            help="Milvus password.",
            key="milvus_password_input"
        )
        if milvus_password_input:
            st.session_state.milvus_password = milvus_password_input
        
        # Milvus cloud link
        st.caption("💡 [Get Milvus cloud (Zilliz Cloud)](https://zilliz.com/cloud)")
        
        st.markdown("---")
        
        # Get config (user input has highest priority)
        config = get_config(
            user_dashscope_key=st.session_state.dashscope_key,
            user_milvus_uri=st.session_state.milvus_uri,
            user_milvus_user=st.session_state.milvus_user,
            user_milvus_password=st.session_state.milvus_password
        )
        
        # Validate config
        config_ok = True
        if not config["dashscope_key"]:
            st.error("❌ DashScope API Key is not set.")
            st.info("Please enter your DashScope API Key in the field above.")
            config_ok = False
        else:
            st.success(f"✅ DashScope API Key is set ({len(config['dashscope_key'])} characters).")
        
        if not config["milvus_uri"] or not config["milvus_user"] or not config["milvus_password"]:
            st.error("❌ Milvus configuration is not set.")
            st.info("Please enter Milvus configuration in the fields above.")
            config_ok = False
        else:
            st.success("✅ Milvus configuration is set.")
        
        st.markdown("---")
        st.markdown("### 📖 How to use")
        st.markdown("""
        1. **Configure API Key**: Enter your DashScope API Key and Milvus configuration above.
        2. **First-time use**: Upload a PDF or TXT document to build the vector index.
        3. **Ask questions**: Enter your question below; the system will retrieve relevant context and generate an answer.
        """)
        
        st.markdown("---")
        st.markdown("### 💡 Notes")
        st.info("""
        **Configuration notes:**
        - All configuration is stored only in the current browser session.
        - You will need to re-enter configuration after refreshing the page.
        - Configuration is not uploaded to the server; it is intended to be safe and private.
        """)
    
    if not config_ok:
        st.warning("⚠️ Please complete the configuration before using the app.")
        return
    
    # 初始化组件
    try:
        with st.spinner("🔄 Initializing LLM and embeddings..."):
            graph_llm, llm = initialize_llm(config)
            embeddings = initialize_embeddings(config)
        
        # Main UI: tabs
        tab1, tab2 = st.tabs(["💬 Q&A", "📄 Document management"])
        
        with tab1:
            st.header("💬 Q&A")
            
            # Load vector store
            vectorstore = load_vectorstore(config, embeddings)
            
            if vectorstore is None:
                st.warning("⚠️ Vector index has not been built. Please upload documents on the 'Document management' tab first.")
            else:
                # Question input
                question = st.text_area(
                    "Enter your question:",
                    height=100,
                    placeholder="例如：What CD4+ T helper subsets are discussed in this article?"
                )
                
                # Retrieval parameters
                with st.expander("🔧 Retrieval parameters"):
                    k = st.slider("Number of documents to retrieve (k)", min_value=1, max_value=20, value=8, step=1)
                    max_context_chars = st.slider("Maximum context length", min_value=1000, max_value=10000, value=6000, step=500)
                
                if st.button("🚀 Submit question", type="primary"):
                    if not question.strip():
                        st.warning("Please enter a question.")
                    else:
                        with st.spinner("🔍 Searching relevant documents..."):
                            # Retrieve documents
                            retriever = vectorstore.as_retriever(search_kwargs={"k": k})
                            docs = retriever.invoke(question)
                            
                            # Show retrieved documents
                            with st.expander(f"📚 Retrieved {len(docs)} relevant document chunks", expanded=False):
                                for i, doc in enumerate(docs[:5], 1):
                                    preview = doc.page_content.replace("\n", " ")
                                    preview = (preview[:300] + "...") if len(preview) > 300 else preview
                                    st.markdown(f"**Chunk {i}** (length: {len(doc.page_content)} characters)")
                                    st.text(preview)
                                    st.markdown("---")
                            
                            # 构建上下文
                            seen = set()
                            unique_texts = []
                            for doc in docs:
                                text = (doc.page_content or "").strip()
                                if not text:
                                    continue
                                key = text[:200]
                                if key in seen:
                                    continue
                                seen.add(key)
                                unique_texts.append(text)
                            
                            context = "\n\n".join(unique_texts)
                            context = context[:max_context_chars]
                        
                        with st.spinner("🤖 Generating answer..."):
                            # Create RAG chain
                            rag_chain = create_rag_chain(graph_llm)
                            
                            # Generate answer
                            generation = rag_chain.invoke({"context": context, "question": question})
                            
                            # Show answer
                            st.markdown("### 💡 Answer")
                            st.markdown(generation)
        
        with tab2:
            st.header("📄 Document management")
            
            st.markdown("### 📤 Upload documents")
            uploaded_file = st.file_uploader(
                "Choose a PDF or TXT file",
                type=["pdf", "txt"],
                help="Supports PDF and TXT formats."
            )
            
            if uploaded_file is not None:
                st.info(f"📄 Selected file: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
                
                collection_name = st.text_input(
                    "Collection name",
                    value="company_milvus",
                    help="Name of the Milvus collection used to store the vector index."
                )
                
                if st.button("🔨 Build vector index", type="primary"):
                    with st.spinner("🔄 Processing document and building vector index..."):
                        try:
                            vectorstore, num_chunks = process_uploaded_file(
                                uploaded_file, embeddings, config, collection_name
                            )
                            st.success(f"✅ Vector index built successfully! Processed {num_chunks} document chunks.")
                            st.info("💡 You can now use this index on the 'Q&A' tab to ask questions.")
                            
                            # 清除缓存，强制重新加载
                            load_vectorstore.clear()
                            
                        except Exception as e:
                            st.error(f"❌ Build failed: {str(e)}")
                            st.exception(e)
    
    except Exception as e:
        st.error(f"❌ Initialization failed: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
