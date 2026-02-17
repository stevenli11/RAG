# RAG System

<div align="center">
  <h3>🤖 AI-Powered Retrieval-Augmented Generation System</h3>
  <p><strong>Intelligent document Q&A with multimodal support and advanced query processing</strong></p>
</div>

---

## Introduction

A **Retrieval-Augmented Generation (RAG)** system built with **Streamlit**, **LangChain**, **DashScope LLM** (Alibaba Cloud), and **Milvus** vector database. The system enables intelligent question-answering over your documents with support for multiple file formats, OCR capabilities for images and scanned documents, and adaptive query processing.

### Key Features

- **📄 Multi-Format Document Support**: PDF, TXT, and image files (JPG, PNG, BMP, TIFF)
- **🖼️ Intelligent OCR**: Automatic text extraction from images and scanned documents using DashScope Vision API (qwen-vl-max)
- **🔍 Smart Query Rewriting**: Automatic query optimization for better retrieval results
- **💬 Context-Aware Chat**: Multi-turn conversations with chat history integration
- **🎯 Adaptive Prompting**: Question type classification with specialized prompts (factual, experiment design, comparison, analytical)
- **⚡ Streaming Responses**: Real-time answer generation with token-by-token streaming
- **🗄️ Flexible Storage**: Support for both personal and shared Milvus databases
- **🔧 Configurable Retrieval**: Adjustable document count (k) and context length parameters

## Quick Navigation

| Topic | Description |
|-------|-------------|
| 🚀 [Quick Start](#quick-start) | Get up and running in minutes |
| 📚 [Features](#features) | Detailed capabilities overview |
| 🛠️ [Installation](#installation) | Setup and configuration |
| 📖 [Usage Guide](#usage-guide) | How to use the system |
| 🏗️ [Architecture](#architecture) | System design and components |
| 🔧 [Configuration](#configuration) | API keys and settings |

## Features

### Core Capabilities

#### 1. Document Processing

**Multi-Format Support:**
- **PDF Files**: Direct text extraction for regular PDFs, automatic OCR for scanned PDFs
- **Text Files**: Plain text document processing
- **Image Files**: OCR-based text extraction from JPG, PNG, BMP, TIFF formats

**Processing Pipeline:**
```
Document Upload → Format Detection → Text Extraction (with OCR if needed) 
→ Text Cleaning → Chunking → Embedding → Vector Storage (Milvus)
```

**Features:**
- Automatic handling of special characters and encoding issues
- Metadata field cleaning for Milvus compatibility
- Configurable collection names for organized document management
- PyMuPDF-based image extraction from PDFs for OCR processing

#### 2. Intelligent Query Processing

**Query Rewriting:**
- Automatic query enhancement for better retrieval results
- Context-aware rewriting using conversation history
- Handling of ambiguous references and follow-up questions

**Question Classification:**
Four specialized question types with tailored prompts:
1. **Factual Questions**: Direct information retrieval with precise answers
2. **Experiment Design Questions**: Structured experimental planning with methodology guidance
3. **Comparison Questions**: Side-by-side analysis with structured comparison tables
4. **Analytical Questions**: In-depth reasoning with multi-perspective analysis

**Example Prompts:**
- Factual: "What is the role of cytokines?"
- Experiment: "How should I design an experiment to test...?"
- Comparison: "Compare method A and method B"
- Analytical: "Why does this phenomenon occur?"

#### 3. Conversational RAG

**Multi-Turn Chat:**
- Maintains conversation context (last 10 turns for rewriting, up to 20 turns stored)
- Smart history pruning to avoid token overflow
- Seamless integration of chat history into prompts

**Chat Features:**
- Real-time streaming responses with visual feedback
- Retrieved document preview with expandable chunks
- Chat history export to Markdown format
- One-click history clearing

#### 4. Vector Retrieval

**Milvus Integration:**
- High-performance vector similarity search
- Support for both cloud and self-hosted Milvus instances
- Configurable collection management

**Retrieval Strategy:**
- Top-k document retrieval (configurable 1-20)
- Deduplication of retrieved chunks
- Context length optimization (configurable 1000-10000 characters)
- Source document tracking with metadata

### Advanced Features

#### OCR Processing

**DashScope Vision API Integration:**
- Uses qwen-vl-max model for high-accuracy text recognition
- Base64 image encoding for API transmission
- Structured prompt engineering for optimal text extraction
- Graceful fallback handling for API failures

**Supported Scenarios:**
- Scanned research papers and academic documents
- Screenshots and presentations
- Handwritten notes (with varying accuracy)
- Multi-language documents

#### Dual LLM Strategy

**Cost-Optimized Architecture:**
- **Large Model (qwen-plus)**: Answer generation with streaming support
- **Small Model (qwen-flash)**: Query rewriting and classification for cost efficiency

**Benefits:**
- Reduced API costs by using smaller models for lightweight tasks
- Maintained high quality for final answer generation
- Faster processing for query preprocessing steps

## Installation

### Prerequisites

- Python 3.9+
- DashScope API Key (from Alibaba Cloud)
- Milvus instance (Zilliz Cloud or self-hosted) - optional for personal use

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/stevenli11/RAG.git
cd RAG
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables (optional):**

Create a `.env` file in the project root:
```env
DASHSCOPE_API_KEY=your_dashscope_api_key
DASHSCOPE_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
MILVUS_URI=your_milvus_uri
MILVUS_USER=your_milvus_user
MILVUS_PASSWORD=your_milvus_password
```

Alternatively, configure via Streamlit secrets (`.streamlit/secrets.toml`) or UI input.

## Quick Start

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

### First-Time Setup

1. **Configure API Key** (in sidebar):
   - Enter your DashScope API Key
   - [Get a DashScope API Key](https://dashscope.console.aliyun.com/)

2. **Configure Milvus** (optional):
   - **Without Milvus config**: Uses the author's pre-built database (demo mode)
   - **With your own Milvus**: Enter URI, username, and password
   - [Get Milvus Cloud (Zilliz Cloud)](https://zilliz.com/cloud)

3. **Upload Documents** (if using your own Milvus):
   - Navigate to "📄 Document Management"
   - Upload PDF, TXT, or image files
   - Specify collection name
   - Click "🔨 Build vector index"

4. **Start Chatting**:
   - Navigate to "💬 Chat"
   - Ask questions about your documents
   - View retrieved sources and chat history

### Usage Examples

**Example 1: Factual Query**
```
User: What are cytokines?
System: [Retrieves relevant chunks] → [Generates precise definition with context]
```

**Example 2: Experiment Design**
```
User: How should I design an experiment to test T cell activation?
System: [Retrieves methodology] → [Generates structured experimental plan]
```

**Example 3: Follow-up Question**
```
User: What is RAG?
System: Retrieval-Augmented Generation is a technique that...
User: How does it differ from standard LLMs?
System: [Uses conversation history to rewrite query] → [Generates comparison]
```

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                      │
│  (Chat Interface + Document Management + Configuration)  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                          │
┌───────▼────────┐        ┌───────▼────────┐
│  Query Pipeline │        │ Document Pipeline│
│                 │        │                  │
│ 1. Rewrite Query│        │ 1. Upload File   │
│ 2. Classify Type│        │ 2. Extract Text  │
│ 3. Retrieve Docs│        │ 3. OCR (if needed)│
│ 4. Generate Ans │        │ 4. Chunk & Embed │
└────────┬────────┘        └────────┬─────────┘
         │                          │
    ┌────▼────┐                ┌────▼────┐
    │DashScope│                │ Milvus  │
    │  LLMs   │◄───────────────┤ Vector  │
    │(qwen-*) │   Embedding    │   DB    │
    └─────────┘                └─────────┘
```

### Key Technologies

- **Frontend**: Streamlit (interactive web interface)
- **LLM Provider**: Alibaba Cloud DashScope
  - qwen-plus: Answer generation (streaming)
  - qwen-flash: Query rewriting & classification
  - qwen-vl-max: OCR text extraction
- **Embeddings**: DashScope text-embedding-v4
- **Vector Database**: Milvus (high-performance similarity search)
- **Framework**: LangChain (RAG orchestration)
- **Document Processing**:
  - PyPDF: PDF text extraction
  - PyMuPDF (fitz): PDF to image conversion
  - PIL: Image handling

### Data Flow

**Query Processing Flow:**
```
User Question → Query Rewriter (qwen-flash) → Rewritten Query
→ Vector Retriever (Milvus) → Top-k Documents
→ Context Builder (deduplication + truncation)
→ Question Classifier (qwen-flash) → Question Type
→ Prompt Selector → Specialized Prompt
→ Answer Generator (qwen-plus, streaming) → Final Answer
```

**Document Processing Flow:**
```
File Upload → Format Detection → Text Extraction
→ [PDF: PyPDF or OCR] [Image: OCR via qwen-vl-max]
→ Text Cleaning → RecursiveCharacterTextSplitter
→ Chunk Creation → Embedding (text-embedding-v4)
→ Milvus Storage (with metadata)
```

## Configuration

### API Keys

**DashScope API Key** (Required):
- Register at [Alibaba Cloud DashScope](https://dashscope.console.aliyun.com/)
- Create an API key with access to:
  - qwen-plus (for answer generation)
  - qwen-flash (for query processing)
  - qwen-vl-max (for OCR)
  - text-embedding-v4 (for embeddings)

**Milvus Configuration** (Optional):
- **Option 1**: Use author's pre-built database (demo mode, no configuration needed)
- **Option 2**: Use your own Milvus instance
  - Cloud: [Zilliz Cloud](https://zilliz.com/cloud) (managed service)
  - Self-hosted: [Milvus Installation Guide](https://milvus.io/docs/install_standalone-docker.md)

### Retrieval Parameters

**Number of Documents (k)**: 1-20
- Default: 8
- Higher values retrieve more context but may introduce noise
- Recommended: 5-10 for most use cases

**Max Context Length**: 1000-10000 characters
- Default: 6000
- Limits total context to avoid token overflow
- Adjust based on document complexity and query needs

### Collection Management

**Collection Naming Rules** (Milvus requirements):
- Only letters, numbers, and underscores allowed
- Cannot start with a digit
- Auto-cleaning: `my-collection!` → `my_collection`

**Recommended Structure**:
- Separate collections for different document types or projects
- Example: `research_papers`, `lab_protocols`, `meeting_notes`

## File Structure

```
RAG/
├── app.py                    # Main Streamlit application
│   ├── Helper Functions      # Text cleaning, metadata formatting
│   ├── Config Management     # API key and database configuration
│   ├── LLM Initialization    # DashScope model setup
│   ├── Embedding Setup       # text-embedding-v4 initialization
│   ├── Vectorstore Loading   # Milvus connection and retrieval
│   ├── OCR Processing        # Image and scanned PDF text extraction
│   ├── Document Processing   # Multi-format file handling
│   ├── Query Rewriting       # Context-aware query enhancement
│   ├── Question Classification # Type detection for adaptive prompts
│   ├── Prompt Templates      # Specialized prompts for each question type
│   ├── RAG Chain Creation    # LangChain pipeline assembly
│   └── Main UI               # Chat and document management interfaces
│
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── README_STREAMLIT.md       # Streamlit-specific documentation
├── LICENSE                   # MIT License
│
├── LangChain/                # LangChain examples and utilities
├── LangChain.py              # Additional LangChain implementations
├── Naive RAG/                # Basic RAG implementation reference
│
└── Cytokine Regulation and Function in T Cells.pdf
                              # Example document for testing
```

## Usage Guide

### Document Management

1. **Navigate to Document Management**:
   - Click "📄 Document Management" in sidebar

2. **Upload a Document**:
   - Drag and drop or click to browse
   - Supported: PDF, TXT, JPG, PNG, BMP, TIFF

3. **Configure Collection** (optional):
   - Enter collection name (default: `company_milvus`)
   - Names auto-cleaned to meet Milvus requirements

4. **Build Index**:
   - Click "🔨 Build vector index"
   - Wait for processing (OCR may take time)
   - Confirmation message on success

### Chat Interface

1. **Navigate to Chat**:
   - Click "💬 Chat" in sidebar

2. **Ask Questions**:
   - Type your question in the chat input
   - System automatically:
     - Rewrites query for better retrieval
     - Searches documents
     - Generates streaming answer

3. **View Sources**:
   - Expand "📚 Retrieved X document chunks"
   - See source text previews with character counts

4. **Manage History**:
   - "💾 Save Chat History": Export to Markdown
   - "🗑️ Clear Chat History": Reset conversation

### Advanced Settings

**Chat Settings** (in sidebar, collapsed by default):
- **Number of documents (k)**: Control retrieval breadth
- **Max context length**: Control context size

**Configuration** (in sidebar, collapsed by default):
- Update API keys on the fly
- Switch between Milvus instances
- View connection status

## Tips and Best Practices

### Document Preparation

- **PDF Files**: Ensure text is selectable (not scanned) for faster processing
- **Images**: Use high-resolution, clear images for better OCR accuracy
- **Large Files**: Consider splitting very large documents for better retrieval granularity

### Query Formulation

- **Be Specific**: "What is the role of IL-2 in T cell activation?" vs "Tell me about IL-2"
- **Use Follow-ups**: Leverage conversation history for contextual questions
- **Experiment Type**: Phrase as design questions for structured plans

### Collection Organization

- Separate collections by topic or project for cleaner retrieval
- Use descriptive names: `immunology_papers` vs `collection1`
- Rebuild collections when adding significantly different document types

### Performance Optimization

- Start with k=5 documents, increase if answers lack context
- Use lower context limits for faster responses
- Clear chat history periodically to reduce processing overhead

## Troubleshooting

### Common Issues

**Issue**: "Failed to load existing collection"
- **Solution**: Upload a document first to create the collection, or check Milvus configuration

**Issue**: OCR processing takes too long
- **Solution**: OCR is compute-intensive; for large scanned PDFs, consider pre-processing with desktop OCR tools

**Issue**: Answers not relevant to documents
- **Solution**: Increase k (number of documents), check if correct collection is selected, ensure documents are properly indexed

**Issue**: "DashScope API Key is not set"
- **Solution**: Enter API key in sidebar configuration, or set in `.env` file

### Error Messages

- **"Milvus configuration is not set"**: Enter Milvus URI, username, and password, or skip to use demo mode
- **"Failed to initialize embeddings"**: Check DashScope API key and network connection
- **"Unable to preview image"**: Image format may be corrupted; try re-uploading

## Requirements

### Python Dependencies

See [`requirements.txt`](requirements.txt) for the complete and authoritative list of dependencies.

Key packages include:
- **streamlit**: Web UI framework
- **langchain-openai, langchain-community, langchain-milvus, langchain-core**: RAG orchestration
- **dashscope**: Alibaba Cloud DashScope SDK (LLMs and embeddings)
- **pymilvus**: Milvus vector database client
- **pypdf, pymupdf**: PDF processing
- **pillow**: Image handling

### External Services

- **DashScope Account**: [Sign up here](https://dashscope.console.aliyun.com/)
- **Milvus** (optional for personal use):
  - Cloud: [Zilliz Cloud](https://zilliz.com/cloud)
  - Self-hosted: [Milvus Standalone](https://milvus.io/docs/install_standalone-docker.md)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Areas for Contribution

- Additional file format support (DOCX, PPTX, etc.)
- Enhanced OCR preprocessing (image quality improvement)
- Support for more LLM providers
- Advanced retrieval strategies (hybrid search, reranking)
- Multi-language document support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [LangChain](https://www.langchain.com/) for RAG orchestration
- Powered by [Alibaba Cloud DashScope](https://dashscope.aliyun.com/) LLMs
- Vector storage by [Milvus](https://milvus.io/)
- UI framework by [Streamlit](https://streamlit.io/)

---

**For additional implementation details, see:**
- [Streamlit Documentation](README_STREAMLIT.md)
- [LangChain Examples](./LangChain/)
- [Naive RAG Reference](./Naive%20RAG/)
