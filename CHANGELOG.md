# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-05

### Added
- **OCR Model Support**: Integrated OCR capabilities using DashScope qwen-vl-max model
  - Added support for image file uploads (JPG, JPEG, PNG, BMP, TIFF, TIF)
  - Automatic OCR processing for scanned PDF documents
  - Intelligent fallback: tries direct text extraction first, uses OCR when needed
  - Enhanced file type support for richer document processing

- **Question Classification System**: Implemented intelligent question classification with tailored prompts
  - Automatic classification of questions into three categories:
    - **Knowledge**: For explanations, definitions, and general knowledge queries
    - **Experiment**: For experimental design, protocols, and research plans
    - **General**: For other types of questions
  - Dynamic prompt selection based on question type
  - Optimized responses with category-specific prompt templates
  - Improved answer quality through context-aware prompting

### Improved
- Better support for diverse document types and formats
- Enhanced text extraction accuracy for scanned documents
- More contextually appropriate responses based on question classification

## [1.0.0] - Initial Release

### Added
- Basic RAG (Retrieval Augmented Generation) system
- Integration with LangChain and DashScope LLM
- Milvus vector database for document storage and retrieval
- Streamlit web interface for user interaction
- Support for PDF and TXT file uploads
- Document chunking and embedding generation
- Question answering based on uploaded documents
