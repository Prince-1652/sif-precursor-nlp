import re

NEGATION_WORDS = {"not", "no", "without", "failed", "missing", "bypassed", "absent"}
POSITIVE_WORDS = {"completed", "verified", "confirmed", "correctly", "properly"}

def get_context_multiplier(phrase_context: str) -> float:
    """
    Returns a multiplier for the rule weight based on surrounding context.
    If positive context around a barrier -> it worked (weight reduces).
    If negative context around a barrier -> it failed (weight increases).
    """
    words = set(re.findall(r'\b\w+\b', phrase_context.lower()))
    
    if words.intersection(NEGATION_WORDS):
        return 1.5  # E.g. "LOTO not applied" increases risk
        
    if words.intersection(POSITIVE_WORDS):
        return 0.2  # E.g. "LOTO verified" lowers risk
        
    return 1.0
