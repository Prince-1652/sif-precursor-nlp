import pytest
from app.engines.decision import decision_engine

def test_decision_layer_valid():
    sif_res = {"sif_potential": True, "score": 0.9, "confidence": 0.9, "risk_band": "HIGH"}
    lsr_res = []
    ent_res = []
    
    state, contradictions = decision_engine.orchestrate(sif_res, lsr_res, ent_res)
    assert len(contradictions) == 0
    assert state == "AUTO_ACCEPTED_HIGH_CONFIDENCE"

def test_decision_layer_invalid():
    sif_res = {} # missing sif_potential
    lsr_res = []
    ent_res = []
    
    state, contradictions = decision_engine.orchestrate(sif_res, lsr_res, ent_res)
    assert state == "REVIEW_REQUIRED"

def test_decision_layer_contradiction():
    sif_res = {"sif_potential": True, "score": 0.9, "confidence": 0.9, "risk_band": "HIGH"}
    lsr_res = []
    # High SIF but successful barrier and no failed barrier
    ent_res = [{"entity_type": "BARRIER", "status": "SUCCESSFUL"}]
    
    state, contradictions = decision_engine.orchestrate(sif_res, lsr_res, ent_res)
    assert len(contradictions) > 0
    assert state == "REVIEW_RECOMMENDED"

def test_decision_layer_low_risk():
    sif_res = {"sif_potential": False, "score": 0.1, "confidence": 0.9, "risk_band": "LOW"}
    lsr_res = []
    ent_res = []
    
    state, contradictions = decision_engine.orchestrate(sif_res, lsr_res, ent_res)
    assert len(contradictions) == 0
    assert state == "AUTO_ACCEPTED_LOW_RISK"
