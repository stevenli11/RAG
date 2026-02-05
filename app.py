"""
Streamlit RAG Agent Application
基于 LangChain 的 RAG 问答系统，使用 DashScope LLM 和 Milvus 向量数据库
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

# 页面配置
st.set_page_config(
    page_title="RAG 问答助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 辅助函数 ==========

def clean_text(text):
    """清理文本，移除可能导致编码问题的字符"""
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
    """清理 metadata 字段名，使其符合 Milvus 命名规范（只能包含数字、字母和下划线）"""
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
    """从用户输入、Streamlit secrets 或环境变量获取配置"""
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
    """初始化 LLM（缓存）"""
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
    """初始化 Embeddings（缓存）"""
    dashscope.api_key = config["dashscope_key"]
    
    base_embeddings = DashScopeEmbeddings(
        model="text-embedding-v4",
        dashscope_api_key=config["dashscope_key"]
    )
    
    return base_embeddings


@st.cache_resource
def load_vectorstore(config, _embeddings, collection_name="company_milvus"):
    """加载或创建 Milvus 向量存储（缓存）"""
    connection_args = {
        "uri": config["milvus_uri"],
        "user": config["milvus_user"],
        "password": config["milvus_password"],
    }
    
    try:
        # 尝试加载已有的 collection
        vectorstore = Milvus(
            embedding_function=_embeddings,
            collection_name=collection_name,
            connection_args=connection_args
        )
        # 测试是否能正常检索
        test_retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
        test_docs = test_retriever.invoke("test")
        return vectorstore
    except Exception as e:
        st.error(f"⚠️ 无法加载已有的 collection: {e}")
        st.info("💡 如果是首次使用，需要先上传文档并构建向量索引。")
        return None


def process_uploaded_file(uploaded_file, embeddings, config, collection_name="company_milvus"):
    """处理上传的文件并构建向量索引"""
    # 保存临时文件
    temp_file_path = f"/tmp/{uploaded_file.name}"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        # 加载文档
        if uploaded_file.name.endswith('.pdf'):
            loader = PyPDFLoader(temp_file_path)
            documents = loader.load()
        else:
            loader = TextLoader(temp_file_path, encoding='utf-8')
            documents = loader.load()
        
        # 清理文档
        for doc in documents:
            doc.page_content = clean_text(doc.page_content)
            if doc.metadata:
                cleaned_metadata = {}
                for key, value in doc.metadata.items():
                    # 清理字段名，使其符合 Milvus 命名规范
                    cleaned_key = clean_metadata_key(key)
                    if isinstance(value, str):
                        cleaned_metadata[cleaned_key] = clean_text(value)
                    else:
                        cleaned_metadata[cleaned_key] = value
                doc.metadata = cleaned_metadata
        
        # 文本分割
        chunk_size = 250
        chunk_overlap = 30
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        splits = text_splitter.split_documents(documents)
        
        # 再次清理
        cleaned_splits = []
        for doc in splits:
            cleaned_content = clean_text(doc.page_content)
            if cleaned_content.strip():
                doc.page_content = cleaned_content
                # 再次清理 metadata 字段名（分割后的文档可能保留原始 metadata）
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
        
        # 构建向量索引
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
        
        # 清理临时文件
        os.remove(temp_file_path)
        
        return vectorstore, len(splits)
        
    except Exception as e:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise e


def create_rag_chain(graph_llm):
    """创建 RAG Chain"""
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


# ========== 主应用 ==========

def main():
    st.title("🤖 RAG 问答助手")
    st.markdown("基于 LangChain + DashScope + Milvus 的检索增强生成系统")
    
    # 侧边栏：配置检查
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # 初始化 session_state
        if "dashscope_key" not in st.session_state:
            st.session_state.dashscope_key = ""
        if "milvus_uri" not in st.session_state:
            st.session_state.milvus_uri = ""
        if "milvus_user" not in st.session_state:
            st.session_state.milvus_user = ""
        if "milvus_password" not in st.session_state:
            st.session_state.milvus_password = ""
        
        # DashScope API Key 输入
        st.markdown("### 🔑 DashScope API Key")
        dashscope_key_input = st.text_input(
            "DashScope API Key",
            value=st.session_state.dashscope_key,
            type="password",
            help="输入你的阿里云 DashScope API Key",
            key="dashscope_key_input"
        )
        if dashscope_key_input:
            st.session_state.dashscope_key = dashscope_key_input
            st.caption("💡 [获取 DashScope API Key](https://dashscope.console.aliyun.com/)")
        else:
            st.caption("💡 请输入你的 DashScope API Key 以使用本应用")
        
        st.markdown("---")
        
        # Milvus 配置输入
        st.markdown("### 🗄️ Milvus 配置")
        milvus_uri_input = st.text_input(
            "Milvus URI",
            value=st.session_state.milvus_uri,
            type="default",
            help="Milvus 连接 URI",
            key="milvus_uri_input"
        )
        if milvus_uri_input:
            st.session_state.milvus_uri = milvus_uri_input
        
        milvus_user_input = st.text_input(
            "Milvus User",
            value=st.session_state.milvus_user,
            type="default",
            help="Milvus 用户名",
            key="milvus_user_input"
        )
        if milvus_user_input:
            st.session_state.milvus_user = milvus_user_input
        
        milvus_password_input = st.text_input(
            "Milvus Password",
            value=st.session_state.milvus_password,
            type="password",
            help="Milvus 密码",
            key="milvus_password_input"
        )
        if milvus_password_input:
            st.session_state.milvus_password = milvus_password_input
        
        # 添加 Milvus 注册链接
        st.caption("💡 [获取 Milvus 云服务](https://zilliz.com/cloud)")
        
        st.markdown("---")
        
        # 获取配置（优先使用用户输入）
        config = get_config(
            user_dashscope_key=st.session_state.dashscope_key,
            user_milvus_uri=st.session_state.milvus_uri,
            user_milvus_user=st.session_state.milvus_user,
            user_milvus_password=st.session_state.milvus_password
        )
        
        # 检查配置
        config_ok = True
        if not config["dashscope_key"]:
            st.error("❌ DashScope API Key 未设置")
            st.info("请在上方输入框中输入你的 DashScope API Key")
            config_ok = False
        else:
            st.success(f"✅ DashScope API Key 已设置 ({len(config['dashscope_key'])} 字符)")
        
        if not config["milvus_uri"] or not config["milvus_user"] or not config["milvus_password"]:
            st.error("❌ Milvus 配置未设置")
            st.info("请在上方输入框中输入 Milvus 配置信息")
            config_ok = False
        else:
            st.success("✅ Milvus 配置已设置")
        
        st.markdown("---")
        st.markdown("### 📖 使用说明")
        st.markdown("""
        1. **配置 API Key**：在上方输入你的 DashScope API Key 和 Milvus 配置
        2. **首次使用**：上传 PDF 或 TXT 文档构建向量索引
        3. **提问**：在下方输入问题，系统会从文档中检索相关信息并生成答案
        """)
        
        st.markdown("---")
        st.markdown("### 💡 提示")
        st.info("""
        **配置说明：**
        - 所有配置信息仅保存在当前浏览器会话中
        - 刷新页面后需要重新输入
        - 配置信息不会上传到服务器，安全可靠
        """)
    
    if not config_ok:
        st.warning("⚠️ 请先完成配置后再使用")
        return
    
    # 初始化组件
    try:
        with st.spinner("🔄 正在初始化 LLM 和 Embeddings..."):
            graph_llm, llm = initialize_llm(config)
            embeddings = initialize_embeddings(config)
        
        # 主界面：标签页
        tab1, tab2 = st.tabs(["💬 问答", "📄 文档管理"])
        
        with tab1:
            st.header("💬 问答")
            
            # 加载向量存储
            vectorstore = load_vectorstore(config, embeddings)
            
            if vectorstore is None:
                st.warning("⚠️ 向量索引未构建，请先在「文档管理」标签页上传文档")
            else:
                # 问题输入
                question = st.text_area(
                    "请输入您的问题：",
                    height=100,
                    placeholder="例如：What CD4+ T helper subsets are discussed in this article?"
                )
                
                # 检索参数
                with st.expander("🔧 检索参数"):
                    k = st.slider("检索文档数量 (k)", min_value=1, max_value=20, value=8, step=1)
                    max_context_chars = st.slider("最大上下文长度", min_value=1000, max_value=10000, value=6000, step=500)
                
                if st.button("🚀 提交问题", type="primary"):
                    if not question.strip():
                        st.warning("请输入问题")
                    else:
                        with st.spinner("🔍 正在检索相关文档..."):
                            # 检索文档
                            retriever = vectorstore.as_retriever(search_kwargs={"k": k})
                            docs = retriever.invoke(question)
                            
                            # 显示检索到的文档
                            with st.expander(f"📚 检索到 {len(docs)} 个相关文档片段", expanded=False):
                                for i, doc in enumerate(docs[:5], 1):
                                    preview = doc.page_content.replace("\n", " ")
                                    preview = (preview[:300] + "...") if len(preview) > 300 else preview
                                    st.markdown(f"**片段 {i}** (长度: {len(doc.page_content)} 字符)")
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
                        
                        with st.spinner("🤖 正在生成答案..."):
                            # 创建 RAG Chain
                            rag_chain = create_rag_chain(graph_llm)
                            
                            # 生成答案
                            generation = rag_chain.invoke({"context": context, "question": question})
                            
                            # 显示答案
                            st.markdown("### 💡 答案")
                            st.markdown(generation)
        
        with tab2:
            st.header("📄 文档管理")
            
            st.markdown("### 📤 上传文档")
            uploaded_file = st.file_uploader(
                "选择 PDF 或 TXT 文件",
                type=["pdf", "txt"],
                help="支持 PDF 和 TXT 格式"
            )
            
            if uploaded_file is not None:
                st.info(f"📄 已选择文件: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
                
                collection_name = st.text_input(
                    "Collection 名称",
                    value="company_milvus",
                    help="Milvus collection 名称，用于存储向量索引"
                )
                
                if st.button("🔨 构建向量索引", type="primary"):
                    with st.spinner("🔄 正在处理文档并构建向量索引..."):
                        try:
                            vectorstore, num_chunks = process_uploaded_file(
                                uploaded_file, embeddings, config, collection_name
                            )
                            st.success(f"✅ 向量索引构建成功！共处理 {num_chunks} 个文档块")
                            st.info("💡 现在可以在「问答」标签页使用该索引进行提问了")
                            
                            # 清除缓存，强制重新加载
                            load_vectorstore.clear()
                            
                        except Exception as e:
                            st.error(f"❌ 构建失败: {str(e)}")
                            st.exception(e)
    
    except Exception as e:
        st.error(f"❌ 初始化失败: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
