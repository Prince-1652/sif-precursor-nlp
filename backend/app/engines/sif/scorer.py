def calculate_risk_band(score: float) -> str:
    if score >= 0.8:
        return "HIGH"
    elif score >= 0.5:
        return "MEDIUM"
    return "LOW"

def aggregate_scores(evidence_weights: list[float]) -> float:
    """
    Combines individual evidence weights into a final score (0 to 1).
    Uses a simple noisy-OR or max strategy for now.
    """
    if not evidence_weights:
        return 0.0
    
    # We take the maximum evidence weight as the base, and add a small 
    # fractional increase for additional evidence, capped at 1.0
    max_weight = max(evidence_weights)
    additional_evidence = sum(evidence_weights) - max_weight
    
    final_score = max_weight + (additional_evidence * 0.1)
    return min(1.0, final_score)
