from typing import Dict, Any, List

def validate_engine_outputs(sif_result: Dict[str, Any], lsr_results: List[Dict[str, Any]], entity_results: List[Dict[str, Any]]) -> bool:
    """
    Validates that all three engines produced structurally sound output.
    Returns True if valid, False otherwise.
    """
    if not isinstance(sif_result, dict) or "sif_potential" not in sif_result:
        return False
        
    if not isinstance(lsr_results, list):
        return False
        
    if not isinstance(entity_results, list):
        return False
        
    return True
