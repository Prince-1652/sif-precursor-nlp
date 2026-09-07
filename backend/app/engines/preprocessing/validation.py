from typing import List, Tuple
from app.core.config import settings

def validate_text(text: str) -> Tuple[bool, List[str], str]:
    """
    Validates the input text against basic rules like length.
    Returns: (is_valid, list of errors, status_code)
    """
    errors = []
    
    if not text or not text.strip():
        errors.append("Text is empty or whitespace only.")
        return False, errors, "INVALID"
        
    if len(text.strip()) < settings.MIN_REPORT_LENGTH:
        errors.append(f"Text is too short. Minimum length is {settings.MIN_REPORT_LENGTH} characters.")
        return False, errors, "INSUFFICIENT_TEXT"
        
    return True, errors, "READY"
