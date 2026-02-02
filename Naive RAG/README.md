# 📚 Naive RAG (Retrieval Augmented Generation) System

A simple yet complete RAG (Retrieval Augmented Generation) system implementation for retrieving information from academic papers and generating answers using large language models.

## System Overview

The Naive RAG system combines document retrieval with large language model reasoning to enable knowledge-based intelligent Q&A. The system processes academic papers and provides intelligent Q&A services through four steps:

```
Paper Download → Text Extraction → Vector Storage → Query & Answer
```

## Quick Start

### Using Google Colab (Recommended)

The easiest way to run this project is using **Google Colab**, which provides free GPU access and a pre-configured Python environment.

#### Setup Steps:

1. **Open Google Colab**: Go to [Google Colab](https://colab.research.google.com/)

2. **Mount Google Drive** (for data persistence):
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```

3. **Install Dependencies**:
   ```python
   !pip install openreview-py==1.54.7 chromadb sentence-transformers transformers torch vllm==0.13.0 pymupdf
   ```

4. **Upload or Clone the Repository**:
   - Option A: Upload the notebooks to your Google Drive
   - Option B: Clone from GitHub:
     ```python
     !git clone https://github.com/stevenli11/RAG.git
     %cd RAG/Naive\ RAG
     ```

5. **Enable GPU**:
   - Go to `Runtime` → `Change runtime type`
   - Select `T4 GPU` or higher for hardware accelerator
   - Click `Save`

6. **Run the Notebooks in Order**:
   - `step1_get_papers.ipynb` - Download papers (no GPU needed)
   - `step2_read_data.ipynb` - Extract text using DeepSeek-OCR (requires GPU)
   - `step3_build_vectordb.ipynb` - Build vector database (no GPU needed)
   - `step4_query_and_answer.ipynb` - Query and get answers (requires GPU)

### Local Setup

If you prefer to run locally, ensure you have:
- Python 3.8+
- CUDA-capable GPU with at least 8GB VRAM
- 20GB+ free disk space

Install dependencies:
```bash
pip install openreview-py==1.54.7 chromadb sentence-transformers transformers torch vllm==0.13.0 pymupdf
```

## File Descriptions

### Step 1: Get Papers (`step1_get_papers.ipynb`)
- **Function**: Download research papers from OpenReview
- **Main Operations**:
  - Query ICLR 2025 conference papers using OpenReview API v2
  - Batch download paper PDF files
  - Save PDFs to local folder
- **Dependencies**: `openreview-py` (version 1.54.7)
- **Output**: Research paper PDF files

### Step 2: Read Data (`step2_read_data.ipynb`)
- **Function**: Convert PDF files to structured Markdown using LLM
- **Main Operations**:
  - Convert PDFs to high-resolution images (2x scaling)
  - Process images using DeepSeek-OCR vision language model
  - Serve model via vLLM framework
  - Preserve document structure, formulas, and formatting
  - Output structured Markdown files
- **Dependencies**: `deepseek-ai/DeepSeek-OCR`, `vllm` (0.13.0), `PyMuPDF`
- **Output**: Structured paper text in Markdown format

### Step 3: Build Vector Database (`step3_build_vectordb.ipynb`)
- **Function**: Generate text embeddings and build vector database for semantic search
- **Main Operations**:
  - Generate text embedding vectors using Sentence Transformers (all-MiniLM-L6-v2)
  - Initialize ChromaDB vector store
  - Add Markdown documents and their embedding vectors to database
  - Persist vector database
- **Dependencies**: `chromadb`, `sentence-transformers`
- **Output**: Persistent vector database (ChromaDB) containing document embeddings

### Step 4: Query and Answer (`step4_query_and_answer.ipynb`)
- **Function**: Query vector database and generate answers using local large language model
- **Main Operations**:
  - Retrieve relevant documents from ChromaDB based on similarity search (Top-K retrieval)
  - Format retrieved context into prompts
  - Generate answers using local HuggingFace SmolLM3-3B model
  - Display results with source citations
- **Dependencies**: `chromadb`, `transformers`, `torch`, `sentence-transformers`
- **Output**: AI-generated answers with relevant document context citations

## Tech Stack

- **Data Collection**: OpenReview API v2
- **PDF Processing**: DeepSeek-OCR (LLM-based vision language model)
- **Model Serving**: vLLM (0.13.0)
- **Text Embedding**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB
- **Large Language Model**: HuggingFace SmolLM3-3B (local execution)
- **Deep Learning Framework**: PyTorch
- **Development Environment**: Jupyter Notebook / Google Colab

## Usage Workflow

1. **Prerequisites**: Install required dependencies
   ```bash
   pip install openreview-py==1.54.7 chromadb sentence-transformers transformers torch vllm==0.13.0 pymupdf
   ```

2. **Run Step 1**: Download ICLR 2025 conference papers from OpenReview
   - Open `step1_get_papers.ipynb`
   - Modify query parameters to get papers on specific topics
   - Run notebook to download PDF files

3. **Run Step 2**: Convert PDFs to structured Markdown
   - Open `step2_read_data.ipynb`
   - Configure vLLM and DeepSeek-OCR model
   - Run notebook to convert PDFs to Markdown format

4. **Run Step 3**: Build vector database
   - Open `step3_build_vectordb.ipynb`
   - Run notebook to generate embeddings and build vector database

5. **Run Step 4**: Start Q&A
   - Open `step4_query_and_answer.ipynb`
   - Load HuggingFace SmolLM3-3B model (auto-download)
   - Input questions to get intelligent answers based on paper content

## System Features

- ✅ **End-to-End Pipeline**: Complete workflow from data collection to intelligent Q&A
- ✅ **Modular Design**: Each step runs independently for easy debugging and modification
- ✅ **Semantic Retrieval**: Intelligent document retrieval using vector similarity
- ✅ **Context-Aware**: LLM generates answers based on retrieved relevant documents
- ✅ **Local Execution**: Uses local LLM for data privacy protection without API costs
- ✅ **High-Quality Text Extraction**: LLM-based OCR preserves document structure and formulas
- ✅ **Scalability**: Easy to add new data sources or switch models

## Important Notes

1. **Hardware Requirements**: Running DeepSeek-OCR and SmolLM3-3B requires GPU (recommended at least 8GB VRAM)
2. **Data Storage**: Ensure sufficient disk space for PDF files, model weights, and vector database
3. **Network Connection**: Stable internet connection required for downloading papers and initial model loading
4. **Google Colab**: Code developed in Google Colab environment, using Google Drive for data storage

## RAG System Principles

RAG (Retrieval Augmented Generation) combines the advantages of retrieval systems and generative AI:

1. **Retrieval Phase**: Convert user queries to vectors and search for most relevant document fragments in vector database
2. **Augmentation Phase**: Provide retrieved documents as context to the large language model
3. **Generation Phase**: Large language model generates accurate answers based on retrieved context and user questions

Advantages of this approach compared to direct LLM use:
- More accurate answers based on actual document content
- Can cite information sources
- Not limited by LLM training data recency
- Reduces AI hallucination

## Future Improvements

- [ ] Support more document formats (Word, HTML, etc.)
- [ ] Implement more sophisticated text chunking strategies
- [ ] Add multi-turn conversation support
- [ ] Optimize retrieval algorithms (hybrid retrieval, reranking, etc.)
- [ ] Add evaluation metrics and test sets
- [ ] Build web interface

## License

Please refer to the LICENSE file in the project root directory.
