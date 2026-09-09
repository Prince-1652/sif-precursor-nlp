import re

NEGATION_WORDS = {"not", "no", "without", "failed", "missing", "bypassed", "absent"}
POSITIVE_WORDS = {"completed", "verified", "confirmed", "correctly", "properly"}

def get_context_multiplier(phrase_context: str, rule_type: str = "BARRIER") -> float:
    """
    Returns a multiplier for the rule weight based on surrounding context.
    If positive context around a barrier -> it worked (weight reduces).
    If negative context around a barrier -> it failed (weight increases).
    If negative context around a hazard -> it wasn't present (weight reduces).
    """
    words = set(re.findall(r'\b\w+\b', phrase_context.lower()))
    
    has_negation = bool(words.intersection(NEGATION_WORDS))
    has_positive = bool(words.intersection(POSITIVE_WORDS))
    
    if rule_type == "BARRIER":
        if has_negation: return 1.5
        if has_positive: return 0.2
    else:
        # HAZARD, OUTCOME, ACTIVITY
        if has_negation: return 0.2
        
    return 1.0
