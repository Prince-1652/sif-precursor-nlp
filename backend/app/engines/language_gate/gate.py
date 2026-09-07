from enum import Enum
from app.engines.language_gate.detector import LanguageDetectionResult
from app.core.config import settings

class LanguageGateDecision(Enum):
    DETERMINISTIC_ENGLISH = "deterministic_english"
    AI_NORMALIZATION = "ai_normalization"
    INSUFFICIENT_TEXT = "insufficient_text"
    REVIEW_REQUIRED = "review_required"

def decide_routing(detection: LanguageDetectionResult, text_length: int) -> LanguageGateDecision:
    if text_length < settings.MIN_REPORT_LENGTH:
        return LanguageGateDecision.INSUFFICIENT_TEXT
        
    if not detection.is_reliable:
        return LanguageGateDecision.REVIEW_REQUIRED
        
    if detection.language_code == "en" and detection.confidence >= settings.LANGUAGE_CONFIDENCE_THRESHOLD and not detection.is_mixed:
        return LanguageGateDecision.DETERMINISTIC_ENGLISH
        
    return LanguageGateDecision.AI_NORMALIZATION
