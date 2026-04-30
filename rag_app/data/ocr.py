import os
import base64
import logging
import dashscope
from http import HTTPStatus
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
import fitz


logger = logging.getLogger(__name__)

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
                logger.warning("Failed to parse OCR response: %s", e)
                return ""
            
            return ""
        else:
            error_msg = response.message if hasattr(response, 'message') else f"Status code: {response.status_code}"
            logger.warning("OCR API call failed: %s", error_msg)
            return ""
            
    except Exception as e:
        logger.warning("OCR processing failed: %s", e)
        import traceback
        logger.debug("%s", traceback.format_exc())
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
        logger.info("Direct text extraction failed: %s, trying OCR...", e)
    
    # If direct extraction failed or got little text, use OCR
    logger.info("Detected scanned or image PDF, using OCR processing...")
    image_paths = pdf_to_images_for_ocr(pdf_path)
    
    all_text = []
    for i, image_path in enumerate(image_paths, 1):
        logger.info("Processing page %s/%s for OCR", i, len(image_paths))
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
