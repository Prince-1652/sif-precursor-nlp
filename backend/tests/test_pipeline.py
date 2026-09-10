import pytest
from unittest.mock import patch, AsyncMock
from app.engines.preprocessing.pipeline import run_preprocessing
from app.engines.language_gate.detector import LanguageDetector
from app.engines.language_gate.gate import decide_routing
from app.engines.sif.engine import sif_engine
from app.engines.lsr.engine import lsr_engine
from app.engines.entities.engine import entity_engine
from app.engines.decision import decision_engine
import asyncio

@pytest.mark.asyncio
@patch('app.providers.get_ai_provider')
async def test_analyze_pipeline(mock_get_ai_provider):
    # Setup mock to return a dummy provider that raises error if called (since we want deterministic path here)
    mock_provider = AsyncMock()
    mock_get_ai_provider.return_value = mock_provider

    text = "No worker entered the confined space during the shift."
    
    # 1. Preprocessing
    prep_result = run_preprocessing(text)
    assert prep_result.normalized_text != ""
    
    # 2. Language Gate
    detector = LanguageDetector()
    detection = detector.detect(prep_result.normalized_text)
    decision = decide_routing(detection, len(prep_result.normalized_text))
    
    norm_text = prep_result.normalized_text
    
    # 3. Engines
    sif_result, lsr_results, entity_results = await asyncio.gather(
        sif_engine.analyze(norm_text),
        lsr_engine.analyze(norm_text),
        entity_engine.extract(norm_text)
    )
    
    # 4. Decision Orchestration
    review_state, contradictions, updated_sif_result = decision_engine.orchestrate(
        sif_result, lsr_results, entity_results
    )
    
    # Asserts
    assert decision.value == "deterministic_english"
    assert review_state is not None
    assert updated_sif_result is not None
    assert isinstance(lsr_results, list)
    assert isinstance(entity_results, list)
    
    # Verify AI wasn't called
    mock_provider.generate_content.assert_not_called()
