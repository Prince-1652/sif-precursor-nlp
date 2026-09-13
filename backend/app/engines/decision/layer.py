from typing import Dict, Any, List, Tuple
from app.engines.decision.validator import validate_engine_outputs
from app.engines.decision.contradiction import detect_contradictions
from app.engines.decision.review_state import compute_review_state

class DecisionEngine:
    def orchestrate(
        self, 
        sif_result: Dict[str, Any], 
        lsr_results: List[Dict[str, Any]], 
        entity_results: List[Dict[str, Any]]
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """
        Takes the outputs of the 3 brains and determines the final state.
        Returns: (review_state, list of contradictions, updated_sif_result)
        """
        is_valid = validate_engine_outputs(sif_result, lsr_results, entity_results)
        contradictions = []
        if is_valid:
            contradictions = detect_contradictions(sif_result, lsr_results, entity_results)
            
            # Removed blind auto-upgrade to HIGH risk based on LSR matches and failed barriers.
            # It will now fall through to REVIEW_RECOMMENDED.
            
        review_state = compute_review_state(sif_result, contradictions, is_valid)
        
        return review_state, contradictions, sif_result

decision_engine = DecisionEngine()
