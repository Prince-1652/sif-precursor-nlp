from typing import Dict, Any, List

def detect_contradictions(sif_result: Dict[str, Any], lsr_results: List[Dict[str, Any]], entity_results: List[Dict[str, Any]]) -> List[str]:
    """
    Detects contradictions between engine outputs.
    Returns a list of contradiction descriptions. Empty list means no contradictions.
    """
    contradictions = []
    
    is_sif = sif_result.get("sif_potential", False)
    
    # Extract barrier statuses
    barriers = [e for e in entity_results if e.get("entity_type") == "BARRIER"]
    successful_barriers = [b for b in barriers if b.get("status") == "SUCCESSFUL"]
    failed_barriers = [b for b in barriers if b.get("status") == "FAILED"]
    
    # Contradiction 1: SIF is HIGH, but there are only successful barriers and no failed barriers
    if is_sif and successful_barriers and not failed_barriers:
        contradictions.append("High SIF potential predicted, but only successful barriers were found.")
        
    # Contradiction 2: SIF is False, but there are LSR matches and failed barriers
    if not is_sif and len(lsr_results) > 0 and failed_barriers:
        contradictions.append("Low SIF potential predicted, despite LSR matches and failed barriers.")
        
    return contradictions
