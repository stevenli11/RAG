"""
Streamlit RAG Agent Application
RAG QA system built with LangChain, DashScope LLM and Milvus vector database.
"""

import os
import re
import base64
from datetime import datetime
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
from PIL import Image
import fitz  # PyMuPDF

# Page config
st.set_page_config(
    page_title="AIApproach",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== Helper Functions ==========

def clean_text(text):
    """Clean text and remove characters that may cause encoding issues."""
    if not text:
        return ""
    # Remove control characters (except newline, tab, and carriage return)
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    # Remove zero-width characters
    text = re.sub(r'[\u200b-\u200f\u202a-\u202e\u2060-\u206f]', '', text)
    # Ensure text can be properly encoded as UTF-8
    try:
        text.encode('utf-8')
    except UnicodeEncodeError:
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
    return text


def clean_metadata_key(key):
    """Clean metadata field names to satisfy Milvus naming rules (only letters, numbers and underscores)."""
    if not key:
        return "unknown"
    # Replace non-compliant characters with underscores
    # Milvus field names can only contain: numbers, letters, underscores
    cleaned_key = re.sub(r'[^a-zA-Z0-9_]', '_', str(key))
    # Ensure field name is not empty and doesn't start with a digit (if possible)
    if not cleaned_key or cleaned_key[0].isdigit():
        cleaned_key = "field_" + cleaned_key
    return cleaned_key


def clean_collection_name(name):
    """Clean collection name to satisfy Milvus naming rules (only letters, numbers and underscores)."""
    if not name:
        return "company_milvus"
    # Replace non-compliant characters with underscores
    # Milvus collection names can only contain: numbers, letters, underscores
    cleaned_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(name))
    # Remove consecutive underscores
    cleaned_name = re.sub(r'_+', '_', cleaned_name)
    # Remove leading/trailing underscores
    cleaned_name = cleaned_name.strip('_')
    # Ensure collection name is not empty and doesn't start with a digit
    if not cleaned_name:
        cleaned_name = "company_milvus"
    elif cleaned_name[0].isdigit():
        cleaned_name = "collection_" + cleaned_name
    return cleaned_name


def get_config(user_dashscope_key=None, user_milvus_uri=None, user_milvus_user=None, user_milvus_password=None):
    """Get config from user input, Streamlit secrets or environment variables."""
    # Prioritize user-provided configuration
    dashscope_key = user_dashscope_key or ""
    dashscope_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    milvus_uri = user_milvus_uri or ""
    milvus_user = user_milvus_user or ""
    milvus_password = user_milvus_password or ""
    
    # If user hasn't provided input, try reading from Streamlit secrets
    if not dashscope_key or not milvus_uri:
        try:
            secrets = st.secrets
            
            # DashScope API Key (if user hasn't provided)
            if not dashscope_key:
                dashscope_key = secrets.get("DASHSCOPE_API_KEY", "")
                dashscope_base_url = secrets.get("DASHSCOPE_API_BASE", dashscope_base_url)
            
            # Milvus configuration (if user hasn't provided)
            if not milvus_uri:
                milvus_uri = secrets.get("MILVUS_URI", "")
                milvus_user = secrets.get("MILVUS_USER", "")
                milvus_password = secrets.get("MILVUS_PASSWORD", "")
        except (AttributeError, FileNotFoundError, KeyError):
            # Streamlit secrets not available, use environment variables
            pass
    
    # If still not found, fall back to environment variables
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
    
    # Large model for answer generation (with streaming enabled)
    graph_llm = ChatOpenAI(
        temperature=0,
        model_name="qwen-plus",
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
    # Clean collection name to ensure it meets Milvus requirements
    collection_name = clean_collection_name(collection_name)
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


def extract_text_from_image_ocr(image_path, config):
    """
    Extract text from image using DashScope Vision API (qwen-vl).
    Uses qwen-vl-max model which has OCR capabilities.
    """
    try:
        dashscope.api_key = config["dashscope_key"]
        
        # Read image and convert to base64
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Use DashScope MultiModalConversation API
        from dashscope import MultiModalConversation
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "image": f"data:image/png;base64,{image_base64}"
                    },
                    {
                        "text": "Please extract all text content from this image, maintaining the original format and structure. If there is no text in the image, please return 'No text content'."
                    }
                ]
            }
        ]
        
        response = MultiModalConversation.call(
            model="qwen-vl-max",
            messages=messages
        )
        
        if response.status_code == HTTPStatus.OK:
            # Extract text from response
            try:
                # Response structure: response.output.choices[0].message.content
                content = response.output.choices[0].message.content
                
                # Handle different response formats
                if isinstance(content, str):
                    extracted_text = content
                elif isinstance(content, list):
                    # Extract text from list of content items
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict):
                            if "text" in item:
                                text_parts.append(item["text"])
                        elif isinstance(item, str):
                            text_parts.append(item)
                    extracted_text = "\n".join(text_parts)
                else:
                    extracted_text = str(content)
                
                if extracted_text and extracted_text.strip() and extracted_text.strip() != "No text content":
                    return extracted_text.strip()
            except (AttributeError, IndexError, KeyError) as e:
                st.warning(f"Failed to parse OCR response: {str(e)}")
                return ""
            
            return ""
        else:
            error_msg = response.message if hasattr(response, 'message') else f"Status code: {response.status_code}"
            st.warning(f"OCR API call failed: {error_msg}")
            return ""
            
    except Exception as e:
        st.warning(f"OCR processing failed: {str(e)}")
        import traceback
        st.debug(traceback.format_exc())
        return ""


def pdf_to_images_for_ocr(pdf_path):
    """Convert PDF pages to images for OCR processing."""
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        # Use 2x scaling for high resolution
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        image_path = f"/tmp/page_{page_num + 1}.png"
        pix.save(image_path)
        image_paths.append(image_path)
    
    doc.close()
    return image_paths


def process_pdf_with_ocr(pdf_path, config):
    """
    Process PDF: try direct text extraction first, use OCR if needed.
    """
    # First try direct text extraction
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Check if extracted text is meaningful (not empty or too short)
        total_text = " ".join([doc.page_content for doc in documents])
        if len(total_text.strip()) > 100:  # If we got substantial text, use it
            return documents
    except Exception as e:
        st.info(f"Direct text extraction failed: {str(e)}, trying OCR...")
    
    # If direct extraction failed or got little text, use OCR
    st.info("📸 Detected scanned or image PDF, using OCR processing...")
    image_paths = pdf_to_images_for_ocr(pdf_path)
    
    all_text = []
    for i, image_path in enumerate(image_paths, 1):
        st.info(f"Processing page {i}/{len(image_paths)}...")
        text = extract_text_from_image_ocr(image_path, config)
        if text:
            all_text.append(f"\n\n--- Page {i} ---\n\n{text}")
        
        # Clean up temporary image
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Create a single document from OCR results
    full_text = "\n".join(all_text)
    if full_text.strip():
        return [Document(page_content=full_text, metadata={"source": pdf_path, "method": "ocr"})]
    else:
        raise ValueError("OCR failed to extract text content")


def process_uploaded_file(uploaded_file, embeddings, config, collection_name="company_milvus"):
    """Process uploaded file and build vector index. Supports PDF, TXT, and images."""
    # Clean collection name to ensure it meets Milvus requirements
    collection_name = clean_collection_name(collection_name)
    
    # Save temporary file
    temp_file_path = f"/tmp/{uploaded_file.name}"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        # Load documents based on file type
        if file_ext == '.pdf':
            # Try direct extraction first, fallback to OCR
            documents = process_pdf_with_ocr(temp_file_path, config)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            # Image file - use OCR
            st.info("📸 Detected image file, using OCR processing...")
            extracted_text = extract_text_from_image_ocr(temp_file_path, config)
            if not extracted_text.strip():
                raise ValueError("Failed to extract text content from image")
            documents = [Document(page_content=extracted_text, metadata={"source": uploaded_file.name, "method": "ocr"})]
        elif file_ext == '.txt':
            loader = TextLoader(temp_file_path, encoding='utf-8')
            documents = loader.load()
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported formats: PDF, TXT, JPG, PNG, BMP, TIFF")
        
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


def rewrite_query(question, chat_history=None, small_llm=None):
    """
    Rewrite user query to improve retrieval effectiveness.
    
    Functions:
    1. Handle coreference resolution (e.g., "it", "this method")
    2. Optimize query expression for better retrieval
    3. Expand query if needed (optional)
    
    Args:
        question: Current user question
        chat_history: List of previous conversation turns (optional)
        small_llm: Small LLM for query rewriting
    
    Returns:
        Rewritten query string
    """
    if not small_llm:
        # If no small_llm provided, return original question
        return question
    
    try:
        # Build context from chat history if available
        history_context = ""
        if chat_history and len(chat_history) > 0:
            # Use last 3 turns for context
            recent_history = chat_history[-3:] if len(chat_history) > 3 else chat_history
            history_context = "\n".join([
                f"User: {turn.get('user', '')}\nAssistant: {turn.get('assistant', '')}"
                for turn in recent_history
            ])
            history_context = f"Previous conversation:\n{history_context}\n\n"
        
        rewrite_prompt = f"""{history_context}Current question: {question}

Please rewrite this question to be more effective for document retrieval. 
- If the question contains pronouns or references (like "it", "this", "that"), replace them with specific terms from the conversation context.
- Make the question more specific and clear for semantic search.
- Keep the core meaning unchanged.
- Return ONLY the rewritten question, no explanations."""

        response = small_llm.invoke([HumanMessage(content=rewrite_prompt)])
        
        # Extract rewritten query
        if hasattr(response, 'content'):
            rewritten = response.content.strip()
        else:
            rewritten = str(response).strip()
        
        # Remove quotes if present
        rewritten = rewritten.strip('"').strip("'").strip()
        
        # If rewriting failed or returned empty, use original
        if not rewritten or len(rewritten) < 3:
            return question
        
        return rewritten
    
    except Exception as e:
        # On error, return original question
        return question


def classify_question_type(question, small_llm):
    """
    Classify the type of question to select appropriate prompt template.
    Uses small_llm (qwen-flash) for cost-effective classification.
    """
    classification_prompt = f"""Classify the following question into one of these categories:
1. "knowledge" - Questions asking for explanations, introductions, definitions, or general knowledge (e.g., "What is X?", "Explain Y", "Briefly introduce Z")
2. "experiment" - Questions asking for experimental design, protocols, or research plans (e.g., "Design an experiment", "How to study X", "Plan a protocol")
3. "general" - Other types of questions

Question: {question}

Respond with ONLY one word: "knowledge", "experiment", or "general"."""
    
    try:
        response = small_llm.invoke([HumanMessage(content=classification_prompt)])
        
        # Extract content from response
        if hasattr(response, 'content'):
            question_type = response.content.strip().lower()
        else:
            question_type = str(response).strip().lower()
        
        # Extract just the word if response contains extra text
        for word in ["knowledge", "experiment", "general"]:
            if word in question_type:
                question_type = word
                break
        
        # Validate response
        if question_type not in ["knowledge", "experiment", "general"]:
            # Default to general if classification is unclear
            question_type = "general"
        
        return question_type
    except Exception as e:
        # Default to general on error
        return "general"


def get_prompt_template(question_type, include_history=False):
    """Get appropriate prompt template based on question type."""
    
    # Build conversation history section if needed
    history_section = ""
    if include_history:
        history_section = """
Previous conversation history:
{chat_history}

Note: Use the conversation history to understand context and references (like "it", "this method", etc.). However, prioritize information from the current context documents when answering.
"""
    
    if question_type == "knowledge":
        # Knowledge-based Q&A prompt - for explanatory/introductory questions
        # Focus: Teaching, explaining, comprehensive overview
        template = f"""You are an immunology knowledge assistant. Your role is to provide educational, comprehensive explanations based on the provided context from research documents.

Guidelines:
1. Provide a well-structured, educational answer that helps the user understand the topic
2. Start with a brief overview or definition, then elaborate with details from the context
3. Organize information logically (e.g., use sections, bullet points, or numbered lists)
4. Synthesize information from multiple parts of the context into a coherent explanation
5. Use proper scientific terminology and maintain accuracy
6. If the context doesn't fully answer the question, clearly state what can be answered and what information is missing
7. Consider the conversation history to understand context and references{history_section}

Question: {{question}}
Context: {{context}}

Answer:"""
        input_vars = ["question", "context"]
        if include_history:
            input_vars.append("chat_history")
        return PromptTemplate(
            template=template,
            input_variables=input_vars,
        )
    
    elif question_type == "experiment":
        # Experiment design prompt (original)
        template = f"""You are an immunology experiment-planning assistant.
Design an executable experimental plan using ONLY the provided context. Do NOT invent parameters (e.g., concentrations, incubation times, catalog numbers, instrument models) unless explicitly stated in the context.

Rules:
1) If the context has relevant info, propose a minimal, actionable plan tailored to the goal.
2) If critical details are missing, ask up to 3 clarifying questions (only the most critical).
3) Keep the response concise, but prioritize actionability over being short.
4) Consider the conversation history to understand context and references{history_section}

Question: {{question}}
Context: {{context}}

Answer in this format:
- Goal:
- Hypothesis:
- Minimal plan (3-7 steps):
- Controls:
- Readouts:
- Missing critical info (if any):
- Clarifying questions (0-3):"""
        input_vars = ["question", "context"]
        if include_history:
            input_vars.append("chat_history")
        return PromptTemplate(
            template=template,
            input_variables=input_vars,
        )
    
    else:
        # General Q&A prompt - for factual, specific, or other types of questions
        # Focus: Direct, concise, fact-based answers
        template = f"""You are an immunology research assistant. Answer the question directly and accurately based on the provided context from research documents.

Guidelines:
1. Answer the question directly and concisely - get to the point quickly
2. Focus on factual information from the context
3. If the question asks for specific details (numbers, names, methods), extract and present them clearly
4. If the context doesn't contain enough information, state what can be answered and what is missing
5. Keep the answer focused and avoid unnecessary elaboration
6. Consider the conversation history to understand context and references{history_section}

Question: {{question}}
Context: {{context}}

Answer:"""
        input_vars = ["question", "context"]
        if include_history:
            input_vars.append("chat_history")
        return PromptTemplate(
            template=template,
            input_variables=input_vars,
        )


def create_rag_chain(graph_llm, question=None, small_llm=None, chat_history=None):
    """
    Create RAG chain for answering questions with adaptive prompt selection.
    
    Args:
        graph_llm: LLM for generating answers (qwen-plus)
        question: User's question (optional, for question type classification)
        small_llm: Small LLM for question classification (qwen-flash)
        chat_history: List of previous conversation turns (optional)
    """
    # Check if we have chat history
    has_history = chat_history and len(chat_history) > 0
    
    # If question is provided, classify it and select appropriate prompt
    if question and small_llm:
        question_type = classify_question_type(question, small_llm)
        prompt = get_prompt_template(question_type, include_history=has_history)
    elif question:
        # Fallback: use graph_llm for classification if small_llm not provided
        question_type = classify_question_type(question, graph_llm)
        prompt = get_prompt_template(question_type, include_history=has_history)
    else:
        # Default to experiment design prompt (backward compatibility)
        prompt = get_prompt_template("experiment", include_history=has_history)
    
    return prompt | graph_llm | StrOutputParser()


# ========== Main app ==========

def main():
    # Sidebar: configuration
    # Initialize session_state for navigation
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Chat"
        
    # Initialize session_state for configuration
        if "dashscope_key" not in st.session_state:
            st.session_state.dashscope_key = ""
        if "milvus_uri" not in st.session_state:
            st.session_state.milvus_uri = ""
        if "milvus_user" not in st.session_state:
            st.session_state.milvus_user = ""
        if "milvus_password" not in st.session_state:
            st.session_state.milvus_password = ""
        
    # Title and description removed for cleaner interface
    
    # Sidebar: Navigation and Configuration
    with st.sidebar:
        # App name at the top
        st.markdown("# 🤖 AIApproach")
        st.caption("Transforming research from experience-driven to methodology-driven, from trial-and-error waste to optimal solution paths.")
        st.markdown("---")
        
        # Navigation buttons
        if st.button("💬 Chat", use_container_width=True, type="primary" if st.session_state.current_page == "Chat" else "secondary"):
            st.session_state.current_page = "Chat"
            st.rerun()
        
        if st.button("📄 Document Management", use_container_width=True, type="primary" if st.session_state.current_page == "Document Management" else "secondary"):
            st.session_state.current_page = "Document Management"
            st.rerun()
        
        st.markdown("---")
        
        # Configuration section (collapsed by default)
        with st.expander("⚙️ Configuration", expanded=False):
            # DashScope API Key input
            st.markdown("#### 🔑 DashScope API Key")
            dashscope_key_input = st.text_input(
                "DashScope API Key",
                value=st.session_state.dashscope_key,
                type="password",
                help="Enter your DashScope API Key from Alibaba Cloud DashScope.",
                key="dashscope_key_input",
                label_visibility="collapsed"
            )
            if dashscope_key_input:
                st.session_state.dashscope_key = dashscope_key_input
            st.caption("💡 [Get a DashScope API Key](https://dashscope.console.aliyun.com/)")
            
            st.markdown("---")
            
            # Milvus configuration input
            st.markdown("#### 🗄️ Milvus Configuration")
            milvus_uri_input = st.text_input(
                "Milvus URI",
                value=st.session_state.milvus_uri,
                type="default",
                help="Milvus connection URI.",
                key="milvus_uri_input",
                label_visibility="visible"
            )
            if milvus_uri_input:
                st.session_state.milvus_uri = milvus_uri_input
            
            milvus_user_input = st.text_input(
                "Milvus User",
                value=st.session_state.milvus_user,
                type="default",
                help="Milvus username.",
                key="milvus_user_input",
                label_visibility="visible"
            )
            if milvus_user_input:
                st.session_state.milvus_user = milvus_user_input
            
            milvus_password_input = st.text_input(
                "Milvus Password",
                value=st.session_state.milvus_password,
                type="password",
                help="Milvus password.",
                key="milvus_password_input",
                label_visibility="visible"
            )
            if milvus_password_input:
                st.session_state.milvus_password = milvus_password_input
            
            # Milvus cloud link
            st.caption("💡 [Get Milvus cloud (Zilliz Cloud)](https://zilliz.com/cloud)")
            
            st.markdown("---")
            
            # Get config for validation status display (after inputs are processed)
            sidebar_config = get_config(
                user_dashscope_key=st.session_state.dashscope_key,
                user_milvus_uri=st.session_state.milvus_uri,
                user_milvus_user=st.session_state.milvus_user,
                user_milvus_password=st.session_state.milvus_password
            )
            
            # Show validation status
            if not sidebar_config["dashscope_key"]:
                st.error("❌ DashScope API Key is not set.")
            else:
                st.success(f"✅ DashScope API Key is set ({len(sidebar_config['dashscope_key'])} characters).")
            
            if not sidebar_config["milvus_uri"] or not sidebar_config["milvus_user"] or not sidebar_config["milvus_password"]:
                st.error("❌ Milvus configuration is not set.")
            else:
                st.success("✅ Milvus configuration is set.")
        
        # Chat Settings (only show on Chat page, collapsed by default)
        if st.session_state.current_page == "Chat":
            with st.expander("🔧 Chat Settings", expanded=False):
                # Initialize retrieval parameters in session state
                if "retrieval_k" not in st.session_state:
                    st.session_state.retrieval_k = 8
                if "max_context_chars" not in st.session_state:
                    st.session_state.max_context_chars = 6000
                
                st.session_state.retrieval_k = st.slider(
                    "Number of documents (k)",
                    min_value=1,
                    max_value=20,
                    value=st.session_state.retrieval_k,
                    step=1,
                    help="Number of document chunks to retrieve for context"
                )
                
                st.session_state.max_context_chars = st.slider(
                    "Max context length",
                    min_value=1000,
                    max_value=10000,
                    value=st.session_state.max_context_chars,
                    step=500,
                    help="Maximum characters of context to use"
                )
        
        # Help section (collapsed by default)
        with st.expander("📖 How to use", expanded=False):
            st.markdown("""
        1. **Configure API Key**: Enter your DashScope API Key above.  
        2. **Milvus (optional)**:  
           - If you **do not** enter Milvus configuration, the app will use the **author's pre-built Milvus database**.  
           - If you **do** enter your own Milvus URI / User / Password, the app will use **your own Milvus database** for indexing and search.  
        3. **First-time use with your own Milvus**: Upload a PDF or TXT document to build a new vector index in your Milvus instance.
        4. **Ask questions**: Enter your question below; the system will retrieve relevant context and generate an answer.
        """)
        
        with st.expander("💡 Notes", expanded=False):
            st.info("""
        **Configuration notes:**
        - All configuration is stored only in the current browser session.
        - You will need to re-enter configuration after refreshing the page.
        - Configuration is not uploaded to the server; it is intended to be safe and private.
        """)
    
        # Save and Clear Chat History buttons (only show on Chat page)
        if st.session_state.current_page == "Chat":
            # Save Chat History button (only show if there's chat history)
            if "chat_history" in st.session_state and st.session_state.chat_history:
                # Format chat history for download
                chat_content = f"# Chat History\n\n"
                chat_content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                chat_content += "---\n\n"
                
                for i, turn in enumerate(st.session_state.chat_history, 1):
                    chat_content += f"## Turn {i}\n\n"
                    chat_content += f"**User:**\n{turn['user']}\n\n"
                    chat_content += f"**Assistant:**\n{turn['assistant']}\n\n"
                    chat_content += "---\n\n"
                
                st.download_button(
                    label="💾 Save Chat History",
                    data=chat_content,
                    file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    type="secondary",
                    key="save_chat_btn"
                )
            
            # Clear Chat History button
            if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
                if "chat_history" in st.session_state:
                    st.session_state.chat_history = []
                st.rerun()
    
    # Get config (user input has highest priority) - for main content area
    config = get_config(
        user_dashscope_key=st.session_state.dashscope_key,
        user_milvus_uri=st.session_state.milvus_uri,
        user_milvus_user=st.session_state.milvus_user,
        user_milvus_password=st.session_state.milvus_password
    )
    
    # Validate config
    config_ok = True
    if not config["dashscope_key"]:
        config_ok = False
    if not config["milvus_uri"] or not config["milvus_user"] or not config["milvus_password"]:
        config_ok = False
    
    # Main content area based on selected page
    if st.session_state.current_page == "Chat":
        # Chat page (no header for cleaner interface)
        
        # Check if config is OK
        if not config_ok:
            st.warning("⚠️ Please complete the configuration in the sidebar before using the chat.")
            return
        
        # Initialize components
        try:
            with st.spinner("🔄 Initializing LLM and embeddings..."):
                graph_llm, small_llm = initialize_llm(config)
                embeddings = initialize_embeddings(config)
            
            # Initialize chat history in session_state
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            
            # Load vector store
            vectorstore = load_vectorstore(config, embeddings)
            
            if vectorstore is None:
                st.warning("⚠️ Vector index has not been built. Please upload documents on the 'Document Management' page first.")
            else:
                # Display chat history
                if not st.session_state.chat_history:
                    # Show initial greeting
                    with st.chat_message("assistant"):
                        st.write("👋 How may I assist you today?")
                
                # Display all chat messages
                for turn in st.session_state.chat_history:
                    with st.chat_message("user"):
                        st.write(turn["user"])
                    with st.chat_message("assistant"):
                        st.write(turn["assistant"])
                
                # Chat input at the bottom
                question = st.chat_input("Your message")
                
                if question:
                    # Add user message to history first
                    st.session_state.chat_history.append({
                        "user": question,
                        "assistant": ""  # Will be filled after generation
                    })
                    
                    # Get chat history (limit to last 10 turns to avoid token overflow)
                    chat_history = st.session_state.chat_history[-11:-1] if len(st.session_state.chat_history) > 11 else st.session_state.chat_history[:-1]
                    
                    # Format chat history for prompt
                    formatted_history = ""
                    if chat_history:
                        formatted_history = "\n".join([
                            f"User: {turn['user']}\nAssistant: {turn['assistant']}"
                            for turn in chat_history
                        ])
                    
                    # Display user message
                    with st.chat_message("user"):
                        st.write(question)
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        # Step 1: Rewrite query for better retrieval (use chat history)
                        with st.spinner("✏️ Rewriting query..."):
                            rewritten_question = rewrite_query(question, chat_history=chat_history, small_llm=small_llm)
                        
                        # Step 2: Retrieve documents using rewritten query
                        with st.spinner("🔍 Searching documents..."):
                            retriever = vectorstore.as_retriever(search_kwargs={"k": st.session_state.retrieval_k})
                            docs = retriever.invoke(rewritten_question)
                            
                            # Build context
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
                            context = context[:st.session_state.max_context_chars]
                        
                        # Step 3: Generate answer with streaming
                        rag_chain = create_rag_chain(graph_llm, question=question, small_llm=small_llm, chat_history=chat_history)
                        
                        # Prepare input for RAG chain
                        chain_input = {"context": context, "question": question}
                        if formatted_history:
                            chain_input["chat_history"] = formatted_history
                        
                        # Stream answer token by token
                        full_response = ""
                        message_placeholder = st.empty()
                        
                        # Stream the response
                        for chunk in rag_chain.stream(chain_input):
                            full_response += chunk
                            message_placeholder.write(full_response + "▌")
                        
                        # Remove the cursor and display final answer
                        message_placeholder.write(full_response)
                        
                        # Show retrieval info in expander (optional, collapsed)
                        with st.expander(f"📚 Retrieved {len(docs)} document chunks", expanded=False):
                            for i, doc in enumerate(docs[:5], 1):
                                preview = doc.page_content.replace("\n", " ")
                                preview = (preview[:300] + "...") if len(preview) > 300 else preview
                                st.markdown(f"**Chunk {i}** (length: {len(doc.page_content)} characters)")
                                st.text(preview)
                                st.markdown("---")
                        
                        # Update the last message in chat history with the assistant's response
                        st.session_state.chat_history[-1]["assistant"] = full_response
                        
                        # Limit history to last 20 turns
                        if len(st.session_state.chat_history) > 20:
                            st.session_state.chat_history = st.session_state.chat_history[-20:]
                        
                        # Rerun to show the new message
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ Chat initialization failed: {str(e)}")
            st.exception(e)
        
    elif st.session_state.current_page == "Document Management":
        # Document Management page (no header for cleaner interface)
        
        # Check if config is OK for Document Management
        if not config_ok:
            st.warning("⚠️ Please complete the configuration in the sidebar before uploading documents.")
            return
        
        # Initialize embeddings for document processing
        try:
            with st.spinner("🔄 Initializing embeddings..."):
                embeddings = initialize_embeddings(config)
        except Exception as e:
            st.error(f"❌ Failed to initialize embeddings: {str(e)}")
            return
        
        # File uploader (directly displayed, no expander)
        uploaded_file = st.file_uploader(
            "📎 Drag and drop file here or click to browse (uploading files will use your own database, not the author's database)",
            type=["pdf", "txt", "jpg", "jpeg", "png", "bmp", "tiff", "tif"],
            help="Supports PDF, TXT, and image formats. Images and scanned documents will automatically use OCR to recognize text.",
            label_visibility="visible"
        )
        
        # File type information (collapsed by default)
        with st.expander("ℹ️ Supported File Formats", expanded=False):
            st.markdown("""
            **📄 Text Files:**
            - **PDF**: Regular PDF (direct text extraction) or scanned PDF (automatic OCR)
            - **TXT**: Plain text file
            
            **🖼️ Image Files (Automatic OCR):**
            - JPG / JPEG
            - PNG
            - BMP
            - TIFF / TIF
            
            **💡 Tips:**
            - Scanned documents and images will automatically use OCR to recognize text
            - OCR processing may take some time, please be patient
            - For better recognition results, ensure images are clear and text is readable
            """)
            
            if uploaded_file is not None:
                # Detect file type
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                file_type_icon = "📄"
                file_type_desc = "Document"
                processing_method = "Text extraction"
                
                if file_ext == '.pdf':
                    file_type_icon = "📕"
                    file_type_desc = "PDF Document"
                    processing_method = "Text extraction (OCR if scanned)"
                elif file_ext == '.txt':
                    file_type_icon = "📝"
                    file_type_desc = "Text File"
                    processing_method = "Direct reading"
                elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
                    file_type_icon = "🖼️"
                    file_type_desc = "Image File"
                    processing_method = "OCR text recognition"
                
                # Display file information
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"""
                    **{file_type_icon} {file_type_desc}**  
                    📁 File name: `{uploaded_file.name}`  
                    📊 Size: {uploaded_file.size / 1024:.2f} KB  
                    🔧 Processing method: {processing_method}
                    """)
                
                # If it's an image, show preview
                if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
                    try:
                        image = Image.open(uploaded_file)
                        with col2:
                            st.image(image, caption="Image preview", width=150)
                        # Reset file pointer because Image.open() moves it
                        uploaded_file.seek(0)
                    except Exception as e:
                        st.warning(f"Unable to preview image: {str(e)}")
                
                collection_name_input = st.text_input(
                    "Collection name",
                    value="company_milvus",
                    help="Name of the Milvus collection used to store the vector index. Only letters, numbers, and underscores are allowed."
                )
                
                # Clean collection name to ensure it meets Milvus requirements
                collection_name = clean_collection_name(collection_name_input)
                
                # Show warning if name was cleaned
                if collection_name_input != collection_name:
                    st.warning(f"⚠️ Collection name cleaned: `{collection_name_input}` → `{collection_name}` (Milvus only allows letters, numbers, and underscores)")
                
                if st.button("🔨 Build vector index", type="primary"):
                    # Display different processing messages based on file type
                    file_ext = os.path.splitext(uploaded_file.name)[1].lower() if uploaded_file else ""
                    if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
                        spinner_text = "🔄 Using OCR to recognize text in image, please wait..."
                    elif file_ext == '.pdf':
                        spinner_text = "🔄 Processing PDF document (OCR will be used if scanned)..."
                    else:
                        spinner_text = "🔄 Processing document and building vector index..."
                    
                    with st.spinner(spinner_text):
                        try:
                            vectorstore, num_chunks = process_uploaded_file(
                                uploaded_file, embeddings, config, collection_name
                            )
                            st.success(f"✅ Vector index built successfully! Processed {num_chunks} document chunks.")
                            st.info("💡 You can now use this index on the 'Chat' page to ask questions.")
                            
                            # Clear cache to force reload
                            load_vectorstore.clear()
                            
                        except Exception as e:
                            st.error(f"❌ Build failed: {str(e)}")
                            st.exception(e)


if __name__ == "__main__":
    main()
