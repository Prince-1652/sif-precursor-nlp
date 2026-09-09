import re
from dataclasses import dataclass, asdict
from typing import List, Any
from app.engines.sif.rules import SIF_RULES
from app.engines.sif.negation import get_context_multiplier
from app.engines.sif.scorer import aggregate_scores, calculate_risk_band

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
    async def analyze(self, normalized_text: str) -> dict[str, Any]:
        evidence = []
        weights = []
        
        text_lower = normalized_text.lower()
        
        for rule in SIF_RULES:
            # simple keyword pattern matching
            pattern = r'\b' + re.escape(rule.text_pattern) + r'\b'
            matches = list(re.finditer(pattern, text_lower))
            
            for match in matches:
                start, end = match.start(), match.end()
                
                # Get surrounding context window (roughly 5 words before and after)
                context_start = max(0, start - 30)
                context_end = min(len(text_lower), end + 30)
                context = text_lower[context_start:context_end]
                
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

        final_score = aggregate_scores(weights)
        sif_potential = final_score >= 0.8
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
