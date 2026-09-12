import re
from dataclasses import dataclass, asdict
from typing import List, Any
from app.engines.sif.rules import SIF_RULES
from app.engines.sif.negation import get_context_multiplier
from app.engines.sif.scorer import aggregate_scores, calculate_risk_band
from app.engines.nlp_utils import get_token_context

@dataclass
class EvidenceItem:
    text: str
    type: str
    weight: float
    concept: str
    start: int = 0
    end: int = 0

@dataclass
class SIFResult:
    sif_potential: bool
    score: float
    confidence: float
    risk_band: str
    evidence: List[EvidenceItem]
    engine: str = "hybrid_sif_v1"

class SIFEngine:
    def __init__(self):
        self.rules = SIF_RULES
        
        # Meaningful type-based multipliers established via trial and error
        self.TYPE_MULTIPLIERS = {
            "Incident": 1.3,
            "Near Miss": 1.1,
            "Unsafe Act": 0.9,
            "Unsafe Condition": 0.9,
            "Spill": 0.8,
            "Observation": 0.5
        }

    async def analyze(self, normalized_text: str, report_type: str = None) -> dict[str, Any]:
        """
        Calculates a SIF potential score based on deterministic rules and context matching.
        Applies a dynamic risk weighting if report_type is provided.
        """
        evidence = []
        weights = []
        
        text_lower = normalized_text.lower()
        
        for rule in self.rules:
            # Regex pattern matching (allows complex patterns in dictionary)
            pattern = r'\b(?:' + rule.text_pattern + r')\b'
            matches = list(re.finditer(pattern, text_lower))
            
            for match in matches:
                start, end = match.start(), match.end()
                
                # Get surrounding context window (roughly 10 words before and after)
                context = get_token_context(text_lower, start, end, window_size=10)
                
                multiplier = get_context_multiplier(context, rule.type)
                adjusted_weight = min(1.0, rule.base_weight * multiplier)
                
                weights.append(adjusted_weight)
                evidence.append(EvidenceItem(
                    text=rule.text_pattern,
                    type=rule.type,
                    weight=adjusted_weight,
                    concept=rule.concept,
                    start=start,
                    end=end
                ))

        raw_score = aggregate_scores(weights)
        
        # Apply metadata context weighting
        if report_type:
            clean_type = report_type.replace('_', ' ').title()
            type_mult = self.TYPE_MULTIPLIERS.get(clean_type, 1.0)
        else:
            type_mult = 1.0
            
        final_score = min(1.0, raw_score * type_mult)
        
        sif_potential = final_score >= 0.75
        risk_band = calculate_risk_band(final_score)
        
        # Meaningful confidence calculation based on evidence density and weights
        if len(weights) == 0:
            confidence = 1.0 # Very confident it's not SIF
        else:
            avg_weight = sum(weights) / len(weights)
            confidence = min(1.0, 0.5 + (len(weights) * 0.1) + (avg_weight * 0.2))
        
        result = SIFResult(
            sif_potential=sif_potential,
            score=final_score,
            confidence=confidence,
            risk_band=risk_band,
            evidence=evidence
        )
        return asdict(result)

sif_engine = SIFEngine()
