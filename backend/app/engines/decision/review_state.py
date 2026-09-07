from typing import Dict, Any, List

def compute_review_state(sif_result: Dict[str, Any], contradictions: List[str], engines_valid: bool) -> str:
    """
    Computes the final review state for the report processing.
    """
    if not engines_valid:
        return "REVIEW_REQUIRED"
        
    if len(contradictions) > 0:
        return "REVIEW_RECOMMENDED"
        
    confidence = sif_result.get("confidence", 0.0)
    if confidence < 0.5:
        return "INSUFFICIENT_EVIDENCE"
        
    risk_band = sif_result.get("risk_band", "LOW")
    if risk_band == "HIGH" and confidence >= 0.8:
        return "AUTO_ACCEPTED_HIGH_CONFIDENCE"
        
    if risk_band == "LOW":
        return "AUTO_ACCEPTED_LOW_RISK"
        
    return "REVIEW_RECOMMENDED"
