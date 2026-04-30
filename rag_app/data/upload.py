import os
from pathlib import Path
import logging
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_milvus import Milvus
import time
from rag_app.utils.text_cleaning import clean_text, clean_metadata_key, clean_collection_name
from rag_app.data.ocr import process_pdf_with_ocr, extract_text_from_image_ocr


logger = logging.getLogger(__name__)

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
            logger.info("Detected image file, using OCR processing...")
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
        uri = config["milvus_uri"]
        user = config.get("milvus_user", "")
        password = config.get("milvus_password", "")
        token = config.get("milvus_token", "") or (f"{user}:{password}" if user and password else "")
        if not token:
            raise ValueError("Milvus auth is empty. Please set MILVUS_TOKEN (recommended) or MILVUS_USER/MILVUS_PASSWORD.")

        connection_args = {"uri": uri, "token": token, "secure": True}
        vectorstore = None
        last_error = None
        for _ in range(3):
            try:
                vectorstore = Milvus.from_documents(
                    documents=splits,
                    collection_name=collection_name,
                    embedding=embeddings,
                    connection_args=connection_args,
                    #index_params={"index_type": "HNSW", "metric_type": "L2", "params": {"M": 16, "efConstruction": 200}},  # if chunck > 100,000, use HNSW index
                    drop_old=False,
                )
                break
            except Exception as e:
                last_error = e
                time.sleep(1.2)
                continue

        if vectorstore is None:
            raise last_error if last_error else RuntimeError("Milvus indexing failed")
        
        # Remove temporary file
        os.remove(temp_file_path)
        
        return vectorstore, len(splits)
        
    except Exception as e:
        # Remove temporary file on error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise e
