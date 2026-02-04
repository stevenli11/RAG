# 📚 LangChain RAG Agent

A complete RAG (Retrieval-Augmented Generation) Agent implementation using LangChain framework for building intelligent question-answering systems with external knowledge sources.

## 🔍 System Overview

The LangChain RAG Agent leverages the LangChain framework to build a sophisticated RAG system that combines document retrieval, vector search, and large language model reasoning. The system is designed as an immunology experiment-planning assistant that processes academic papers and provides intelligent Q&A services.

```
Document Loading → Text Processing → Vector Storage (Milvus) → RAG Chain → Intelligent Q&A
```

## 🚀 Quick Start

### 📋 Prerequisites

Before running this project, you need to:

1. **Register for API Access**:
   - **DashScope API** (Alibaba Cloud):
     - Visit [DashScope](https://dashscope.aliyun.com/) and register for an account
     - Navigate to API Key management and create a new API key
     - Save your API key (format: `sk-xxxxxxxxxxxxx`)
     - This is required for accessing the Qwen language model and embedding services
   
2. **Register for Milvus Vector Database**:
   - **Zilliz Cloud** (Managed Milvus):
     - Visit [Zilliz Cloud](https://cloud.zilliz.com/) and create a free account
     - Create a new cluster (serverless tier available for free)
     - Obtain your connection URI, username, and password from the cluster details
     - This is required for storing and querying vector embeddings

### 🌐 Using Google Colab (Recommended)

The easiest way to run this project is using **Google Colab**, which provides free GPU access and a pre-configured Python environment.

#### 🛠️ Setup Steps:

1. **Open Google Colab**: Go to [Google Colab](https://colab.research.google.com/)

2. **Mount Google Drive** (for data persistence):
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

3. **Install Dependencies**:
   ```python
   !pip install langchain langchain-openai langchain-text-splitters langchain-community langchain-milvus python-dotenv pymilvus pypdf dashscope
   ```

4. **Upload or Clone the Repository**:
   - Option A: Upload the notebook to your Google Drive
   - Option B: Clone from GitHub:
     ```python
     !git clone https://github.com/stevenli11/RAG.git
     %cd RAG/LangChain
     ```

5. **Configure API Keys**:
   - Create a `.env` file or directly set in the notebook:
     ```python
     DASHSCOPE_API_KEY="your_dashscope_api_key_here"
     MILVUS_URI="your_milvus_uri_here"
     MILVUS_USER="your_milvus_username_here"
     MILVUS_PASSWORD="your_milvus_password_here"
     ```

6. **Run the Notebook**:
   - Open `LangChain.ipynb`
   - Execute cells sequentially from top to bottom

### 💻 Local Setup

If you prefer to run locally:

**System Requirements:**
- Python 3.8+
- 4GB+ RAM
- Stable internet connection for API calls

**Install dependencies:**
```bash
pip install langchain langchain-openai langchain-text-splitters langchain-community langchain-milvus python-dotenv pymilvus pypdf dashscope
```

**Configure environment variables:**
Create a `.env` file in the LangChain directory:
```
DASHSCOPE_API_KEY=your_dashscope_api_key_here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MILVUS_URI=your_milvus_uri_here
MILVUS_USER=your_milvus_username_here
MILVUS_PASSWORD=your_milvus_password_here
```

## 📝 Notebook Overview

The `LangChain.ipynb` notebook implements a complete RAG Agent with the following components:

### 1️⃣ Environment Setup
- **Function**: Load environment variables and configure API access
- **Configuration**:
  - DashScope API key for LLM and embeddings
  - Milvus connection parameters
  - Model selection (Qwen-plus for reasoning)

### 2️⃣ LLM Initialization
- **Function**: Initialize large language models for different tasks
- **Models Used**:
  - `qwen-plus-2025-12-01`: For graph-based reasoning
  - `qwen-plus`: For general RAG tasks
- **Framework**: LangChain's ChatOpenAI wrapper

### 3️⃣ Document Loading
- **Function**: Load documents from various formats
- **Supported Formats**:
  - PDF files (using PyPDFLoader)
  - TXT files (using TextLoader)
- **Sample Document**: "Cytokine Regulation and Function in T Cells.pdf"

### 4️⃣ Text Processing
- **Function**: Split and clean text for optimal retrieval
- **Operations**:
  - Text cleaning (remove control characters)
  - Recursive character-based splitting
  - Chunk size optimization (500 characters with 100 overlap)
- **Tool**: LangChain's RecursiveCharacterTextSplitter

### 5️⃣ Embeddings Generation
- **Function**: Convert text to vector representations
- **Model**: DashScope Embeddings (text-embedding-v1)
- **Output**: Dense vector representations for semantic search

### 6️⃣ Vector Database Storage
- **Function**: Store document embeddings in Milvus vector database
- **Database**: Milvus (via Zilliz Cloud)
- **Collection**: `company_milvus`
- **Features**:
  - Scalable vector storage
  - Fast similarity search
  - Persistent storage

### 7️⃣ RAG Chain Construction
- **Function**: Build retrieval-augmented generation pipeline
- **Components**:
  - Retriever: Fetches relevant documents (top-k=8)
  - Prompt Template: Structures LLM input
  - LLM: Generates context-aware responses
- **Use Case**: Immunology experiment planning assistant

### 8️⃣ Agent State Management
- **Function**: Define agent state for multi-turn conversations
- **Framework**: LangChain's MessagesState
- **Features**: Message history tracking

### 9️⃣ RAG Agent Node
- **Function**: Implement the core RAG logic
- **Capabilities**:
  - Context-based answer generation
  - Clarifying question support
  - Experiment planning assistance

### 🔟 Testing and Validation
- **Function**: Test the RAG Agent with sample queries
- **Example Queries**:
  - "What CD4+ T helper subsets are discussed in this article?"
  - "Design a minimal experiment to study CD4+ T helper cell differentiation."

## 🔧 Tech Stack

- **Framework**: LangChain (orchestration)
- **LLM**: Alibaba Cloud Qwen-plus (via DashScope API)
- **Embeddings**: DashScope text-embedding-v1
- **Vector Database**: Milvus (Zilliz Cloud)
- **Document Loading**: PyPDFLoader, TextLoader
- **Text Processing**: RecursiveCharacterTextSplitter
- **Environment Management**: python-dotenv
- **Development Environment**: Jupyter Notebook / Google Colab

## 📋 Usage Workflow

1. **Prerequisites**: Register for required services
   ```
   ✓ DashScope API account and key
   ✓ Zilliz Cloud (Milvus) account and connection details
   ```

2. **Install Dependencies**:
   ```bash
   pip install langchain langchain-openai langchain-text-splitters langchain-community langchain-milvus python-dotenv pymilvus pypdf dashscope
   ```

3. **Configure Environment**:
   - Set up `.env` file with API keys and database credentials
   - Or set variables directly in the notebook (Cell 4)

4. **Load Documents**:
   - Place your PDF or TXT files in the LangChain directory
   - Update `file_path` variable in Cell 8

5. **Run the Notebook**:
   - Execute cells sequentially from top to bottom
   - Wait for vector database initialization (first run only)

6. **Query the System**:
   - Modify the `question` variable in Cell 18 or Cell 24
   - Execute the test cells to get answers

## ✨ System Features

- ✅ **LangChain Integration**: Leverages powerful LangChain framework for RAG orchestration
- ✅ **Cloud-Based LLM**: Uses Alibaba Cloud's Qwen model for high-quality responses
- ✅ **Scalable Vector Storage**: Milvus provides efficient and scalable vector search
- ✅ **Multi-Format Support**: Handles both PDF and TXT documents
- ✅ **Intelligent Chunking**: Optimized text splitting for better retrieval
- ✅ **Context-Aware Generation**: LLM generates answers based on retrieved context
- ✅ **Interactive Mode**: Supports clarifying questions for better user experience
- ✅ **Domain-Specific**: Customized for immunology experiment planning
- ✅ **Modular Design**: Easy to adapt for other domains or use cases

## ⚠️ Important Notes

1. **API Costs**: 
   - DashScope API charges based on token usage
   - Monitor your usage in the DashScope console
   - Consider using free tier limits for testing

2. **Milvus Storage**:
   - Zilliz Cloud offers free serverless tier
   - Data persists across sessions
   - Monitor storage usage to avoid exceeding limits

3. **Document Size**:
   - Large PDFs may take time to process
   - Consider splitting very large documents
   - Adjust chunk size based on document complexity

4. **Network Requirements**:
   - Stable internet connection required for API calls
   - Vector database requires persistent connection
   - First run may take longer due to model/data initialization

5. **API Key Security**:
   - Never commit API keys to version control
   - Use `.env` files or environment variables
   - Rotate keys regularly for security

## 🔑 API Registration Guide

### DashScope API (Alibaba Cloud)

1. **Visit DashScope Portal**:
   - Go to https://dashscope.aliyun.com/

2. **Create Account**:
   - Sign up using email or phone number
   - Complete verification process

3. **Get API Key**:
   - Navigate to "API Key Management" (API密钥管理)
   - Click "Create API Key" (创建API密钥)
   - Copy and save your API key securely

4. **Documentation**:
   - API Reference: https://help.aliyun.com/zh/model-studio/
   - Embedding API: https://help.aliyun.com/zh/model-studio/text-embedding-synchronous-api

### Milvus/Zilliz Cloud Registration

1. **Visit Zilliz Cloud**:
   - Go to https://cloud.zilliz.com/

2. **Create Account**:
   - Sign up with email or GitHub account
   - Verify your email address

3. **Create Cluster**:
   - Click "Create Cluster"
   - Select "Serverless" tier (free)
   - Choose region (e.g., us-west-1)
   - Wait for cluster initialization (2-3 minutes)

4. **Get Connection Details**:
   - Click on your cluster name
   - Copy the connection URI (format: `https://xxx.serverless.xxx.cloud.zilliz.com`)
   - Create database credentials (username and password)
   - Note: Save these credentials securely

5. **Documentation**:
   - Milvus Docs: https://milvus.io/docs
   - Zilliz Cloud Guide: https://docs.zilliz.com/

## 🧠 RAG System Principles

RAG (Retrieval Augmented Generation) combines the advantages of retrieval systems and generative AI:

1. **Retrieval Phase**: 
   - Convert user query to vector embedding
   - Search Milvus vector database for most similar document chunks
   - Retrieve top-k most relevant documents

2. **Augmentation Phase**: 
   - Provide retrieved documents as context to the LLM
   - Format context using prompt templates
   - Include source citations and metadata

3. **Generation Phase**: 
   - LLM generates answers based on retrieved context
   - Ensures factual accuracy grounded in source documents
   - Can ask clarifying questions for better results

**Advantages over direct LLM use:**
- ✓ More accurate answers based on actual document content
- ✓ Can cite information sources
- ✓ Not limited by LLM training data recency
- ✓ Reduces AI hallucination
- ✓ Easy to update knowledge base without retraining

## 🔮 Future Improvements

- [ ] Support for more document formats (Word, HTML, Markdown, etc.)
- [ ] Implement hybrid retrieval (keyword + semantic)
- [ ] Add re-ranking for better retrieval accuracy
- [ ] Multi-turn conversation with memory
- [ ] Add evaluation metrics and test sets
- [ ] Build web interface using Streamlit or Gradio
- [ ] Support for multiple vector databases
- [ ] Implement caching for faster responses
- [ ] Add support for multi-modal documents (images, tables)

## 📖 Related Resources

- **LangChain Documentation**: https://python.langchain.com/
- **Milvus Documentation**: https://milvus.io/docs
- **DashScope Documentation**: https://help.aliyun.com/zh/model-studio/
- **RAG Best Practices**: https://www.pinecone.io/learn/retrieval-augmented-generation/

## 📄 License

Please refer to the LICENSE file in the project root directory.
