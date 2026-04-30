# Auto-extracted from original RAG/app.py for modular architecture

import re

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

def clean_answer_meta_phrases(text):
    """
    Remove unnecessary meta-phrases that LLM might add to answers.
    This helps keep answers natural without relying on specific prompt restrictions.
    """
    if not text:
        return text
    
    # Patterns to remove: phrases that add unnecessary meta-commentary
    # These are common patterns where LLM adds meta-information about knowledge recency
    patterns_to_remove = [
        # Remove standalone "Current knowledge emphasizes..." type phrases at sentence start
        r'^Current knowledge emphasizes\s+',
        r'^Recent evidence emphasizes\s+',
        r'^Current understanding emphasizes\s+',
        r'^Modern research emphasizes\s+',
        # Remove these phrases when they appear mid-sentence (less aggressive)
        # Only remove if followed by a period and new sentence
        r'\.\s+Current knowledge emphasizes\s+',
        r'\.\s+Recent evidence emphasizes\s+',
        r'\.\s+Current understanding emphasizes\s+',
    ]
    
    cleaned_text = text
    for pattern in patterns_to_remove:
        # Replace with empty string, but preserve sentence structure
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Clean extra spaces while preserving line/paragraph structure
    cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)  # Only compress inline spaces
    cleaned_text = re.sub(r'\.\s+\.', '.', cleaned_text)  # Remove double periods
    # Avoid more than 2 consecutive blank lines
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

