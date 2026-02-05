# Release V1.1.0 - OCR Support & Intelligent Question Classification

## 🎉 Release Highlights

We're excited to announce Version 1.1.0 of the RAG system with two major improvements that significantly enhance the system's capabilities and user experience.

---

## 📸 Feature 1: OCR Model Support

### What's New
Added comprehensive OCR (Optical Character Recognition) support using DashScope's qwen-vl-max model, enabling the system to process a much wider variety of document types.

### Supported File Types
- **Image Files**: 
  - JPG / JPEG
  - PNG
  - BMP
  - TIFF / TIF
- **Scanned PDFs**: Automatic detection and processing
- **Regular PDFs**: Direct text extraction (existing functionality)
- **Text Files**: TXT (existing functionality)

### Technical Details
- **Intelligent Processing**: The system automatically detects whether a PDF contains extractable text or is a scanned document
- **Fallback Strategy**: First attempts direct text extraction, then falls back to OCR if needed
- **Page-by-Page Processing**: For scanned PDFs, each page is processed individually for optimal accuracy
- **High Accuracy**: Leverages DashScope's state-of-the-art vision model for text recognition

### User Experience
- **Automatic Detection**: No manual configuration needed - the system automatically chooses the best processing method
- **Progress Indicators**: Clear feedback during OCR processing
- **Quality Tips**: Recommendations for best results (clear images, readable text)

---

## 🧠 Feature 2: Intelligent Question Classification

### What's New
Implemented an intelligent question classification system that automatically categorizes user questions and applies appropriate prompt templates for more accurate and contextually relevant responses.

### Question Categories

#### 1. Knowledge Questions
- **Type**: Explanatory, educational queries
- **Examples**: "What is X?", "Explain Y", "Introduce Z"
- **Prompt Focus**: Teaching, comprehensive explanations, educational context
- **Use Case**: General knowledge, definitions, conceptual understanding

#### 2. Experiment Questions
- **Type**: Research planning and experimental design
- **Examples**: "Design an experiment for...", "How to study X?", "Create a protocol for..."
- **Prompt Focus**: Practical methodology, step-by-step procedures, research design
- **Use Case**: Experimental protocols, research planning, methodology development

#### 3. General Questions
- **Type**: All other question types
- **Examples**: Various queries not fitting the above categories
- **Prompt Focus**: General purpose assistance
- **Use Case**: Catch-all for diverse query types

### Technical Details
- **Automatic Classification**: LLM-powered categorization without manual labeling
- **Dynamic Prompt Selection**: System automatically selects the optimal prompt template based on classification
- **Context-Aware Responses**: Each category has specialized prompts designed for that question type
- **Fallback Logic**: Defaults to "general" category if classification is uncertain

### Benefits
- **Higher Quality Answers**: Responses are tailored to the specific type of question
- **Better Context**: Prompts are optimized for the question's intent
- **Improved Relevance**: Answers are more aligned with user expectations
- **Seamless Experience**: No user configuration required - works automatically

---

## 🚀 Improvements

### Document Processing
- **Broader Format Support**: From text-only documents to images and scanned files
- **Better Accuracy**: Enhanced text extraction for various document types
- **Smarter Processing**: Automatic method selection based on document characteristics

### Response Quality
- **Contextual Prompting**: Questions receive category-specific prompts
- **Optimized Templates**: Each category has carefully crafted prompt templates
- **Better Alignment**: Responses better match user intent and question type

### User Experience
- **Automated Workflows**: Less manual configuration needed
- **Clear Feedback**: Better progress indicators and status messages
- **Helpful Guidance**: Tips for optimal usage

---

## 📝 Usage Notes

### For Document Upload
- **Clear Images**: For best OCR results, use clear, well-lit images with readable text
- **Processing Time**: OCR processing may take a few moments - please be patient
- **File Size**: Keep images at reasonable resolution for optimal performance

### For Questions
- **Natural Language**: Ask questions naturally - the system will automatically classify them
- **No Special Format**: No need for special prefixes or formatting
- **Contextual Answers**: Different question types will receive appropriately styled responses

---

## 🔧 Technical Stack

- **OCR Engine**: DashScope qwen-vl-max model
- **Question Classification**: LLM-powered categorization
- **Document Processing**: PyMuPDF, PIL, PyPDFLoader
- **RAG Framework**: LangChain with DashScope LLM
- **Vector Store**: Milvus
- **UI**: Streamlit

---

## 📦 Installation & Setup

No changes to installation process. Continue using:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Make sure you have:
- Valid DashScope API key (for OCR and LLM)
- Milvus connection configured
- Required dependencies installed

---

## 🙏 Acknowledgments

Thanks to all contributors and users who provided feedback that helped shape these improvements!

---

## 📚 Documentation

- **Full Changelog**: See [CHANGELOG.md](CHANGELOG.md)
- **Chinese Release Notes**: See [RELEASES.md](RELEASES.md)
- **Version Info**: See [VERSION](VERSION)

---

**Version**: 1.1.0  
**Release Date**: 2026-02-05  
**Previous Version**: 1.0.0
