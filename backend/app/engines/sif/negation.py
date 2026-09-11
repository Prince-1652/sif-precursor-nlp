from app.engines.nlp_utils import detect_status

def get_context_multiplier(phrase_context: str, rule_type: str = "BARRIER") -> float:
    """
    Returns a multiplier for the rule weight based on surrounding context.
    If positive context around a barrier -> it worked (weight reduces).
    If negative context around a barrier -> it failed (weight increases).
    If negative context around a hazard -> it wasn't present (weight reduces).
    """
    status = detect_status(phrase_context)
    
    if rule_type == "BARRIER":
        if status == "FAILED": return 1.5
        if status == "SUCCESSFUL": return 0.2
    else:
        # HAZARD, OUTCOME, ACTIVITY
        if status == "FAILED": return 0.2
        
    return 1.0
