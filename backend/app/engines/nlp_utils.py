import re

# Centralized list of status/negation keywords.
# By making this a single source of truth, all engines will agree on what constitutes a success/failure.
NEGATION_WORDS = {"not", "no", "without", "failed", "missing", "bypassed", "absent", "cannot"}
POSITIVE_WORDS = {"completed", "verified", "confirmed", "correctly", "properly", "used", "successful"}

def get_token_context(text: str, start: int, end: int, window_size: int = 10) -> str:
    """
    Safely extracts a context window of `window_size` tokens (words) around a matched keyword.
    This prevents the 'sliced word' bug where string indexing (e.g. text[start-30:end+30])
    might cut the word 'cannot' into 'not', causing false positive negations.
    """
    if start < 0 or end > len(text):
        return ""

    # Text before the match
    text_before = text[:start]
    # Text after the match
    text_after = text[end:]

    # Find words before using regex. \w+ matches words. We find all words and take the last `window_size`.
    words_before = re.findall(r'\b\w+\b', text_before)
    context_before_words = words_before[-window_size:] if words_before else []

    # Find words after
    words_after = re.findall(r'\b\w+\b', text_after)
    context_after_words = words_after[:window_size] if words_after else []

    # Reconstruct the safe context string
    # We join with spaces. This destroys original punctuation and spacing, but that is fine 
    # for status/negation detection which only looks for keyword presence.
    return " ".join(context_before_words + context_after_words).lower()

def detect_status(context: str) -> str:
    """
    Detects if a context window indicates a SUCCESSFUL or FAILED barrier/action.
    Replaces brittle `any(w in context)` substring checks which falsely matched 'not' inside 'notice'.
    Uses exact word boundary matching.
    """
    # Extract clean alphanumeric tokens to avoid substring matching bugs
    words = set(re.findall(r'\b\w+\b', context.lower()))
    
    has_negation = bool(words.intersection(NEGATION_WORDS))
    has_positive = bool(words.intersection(POSITIVE_WORDS))
    
    if has_negation:
        return "FAILED"
    elif has_positive:
        return "SUCCESSFUL"
        
    return "UNKNOWN"
