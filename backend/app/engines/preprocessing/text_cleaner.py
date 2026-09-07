import re
import unicodedata

def clean_text(text: str) -> str:
    """
    Cleans the input text by:
    1. Normalizing unicode to NFKC
    2. Stripping HTML tags
    3. Removing control characters
    4. Collapsing whitespace
    5. Converting to lowercase
    """
    # 1. Unicode normalization
    text = unicodedata.normalize('NFKC', text)
    
    # 2. Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # 3. Remove control characters (keep newlines and tabs for now, collapse later)
    # Using a simple printable approach or regex
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ['\n', '\t'])
    
    # 4. Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 5. Lowercase
    return text.lower()
