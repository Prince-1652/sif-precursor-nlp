import pytest
from app.engines.language_gate.detector import LanguageDetector
from app.engines.language_gate.gate import decide_routing, LanguageGateDecision
from app.core.config import settings

@pytest.fixture
def detector():
    return LanguageDetector()

def test_english_detection(detector):
    text = "The worker was wearing a harness while climbing the ladder."
    result = detector.detect(text)
    assert result.language_code == "en"
    assert result.confidence > 0.8
    assert not result.is_mixed
    assert result.is_reliable

def test_spanish_detection(detector):
    text = "El trabajador llevaba un arnés mientras subía la escalera."
    result = detector.detect(text)
    assert result.language_code == "es"
    assert result.confidence > 0.8
    assert result.is_reliable

def test_short_text_reliability(detector):
    text = "hi"
    result = detector.detect(text)
    assert not result.is_reliable

def test_routing_decision():
    # Setup mock detection result
    class MockDetection:
        def __init__(self, code, conf, mixed, reliable):
            self.language_code = code
            self.confidence = conf
            self.is_mixed = mixed
            self.is_reliable = reliable

    # Test short text
    result = MockDetection("en", 0.95, False, False)
    assert decide_routing(result, 5) == LanguageGateDecision.INSUFFICIENT_TEXT
    
    # Test high conf english
    result = MockDetection("en", 0.95, False, True)
    assert decide_routing(result, 50) == LanguageGateDecision.DETERMINISTIC_ENGLISH
    
    # Test spanish
    result = MockDetection("es", 0.95, False, True)
    assert decide_routing(result, 50) == LanguageGateDecision.AI_NORMALIZATION
    
    # Test low conf english
    result = MockDetection("en", 0.60, False, True)
    assert decide_routing(result, 50) == LanguageGateDecision.AI_NORMALIZATION
    
    # Test mixed
    result = MockDetection("en", 0.95, True, True)
    assert decide_routing(result, 50) == LanguageGateDecision.AI_NORMALIZATION
