import asyncio
from app.engines.preprocessing.pipeline import run_preprocessing
from app.engines.language_gate.detector import LanguageDetector
from app.engines.language_gate.gate import decide_routing, LanguageGateDecision
from app.providers import get_ai_provider
from app.engines.sif.engine import sif_engine
from app.engines.lsr.engine import lsr_engine
from app.engines.entities.engine import entity_engine
from app.engines.decision import decision_engine
import json

async def main():
    text = "ek electrician binna power off kiye control panel repair kar raha tha"
    print("Preprocessing...")
    prep_result = run_preprocessing(text)
    detector = LanguageDetector()
    detection = detector.detect(prep_result.normalized_text)
    decision = decide_routing(detection, len(prep_result.normalized_text))
    
    norm_text = prep_result.normalized_text
    print(f"Decision: {decision.value}, Norm text: {norm_text}")
    
    if decision not in [LanguageGateDecision.INSUFFICIENT_TEXT, LanguageGateDecision.REVIEW_REQUIRED, LanguageGateDecision.DETERMINISTIC_ENGLISH]:
        provider = get_ai_provider()
        print("Calling AI provider...")
        norm_res = await provider.normalize_text(norm_text)
        norm_text = norm_res.normalized_text
        print(f"AI Normalized text: {norm_text}")
        
    print("Running engines...")
    sif_result, lsr_results, entity_results = await asyncio.gather(
        sif_engine.analyze(norm_text),
        lsr_engine.analyze(norm_text),
        entity_engine.extract(norm_text)
    )
    
    print("Orchestrating...")
    review_state, contradictions, updated_sif_result = decision_engine.orchestrate(sif_result, lsr_results, entity_results)
    print("SUCCESS")

if __name__ == "__main__":
    asyncio.run(main())
