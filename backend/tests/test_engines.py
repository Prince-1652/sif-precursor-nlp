import pytest
from app.engines.sif.engine import sif_engine
from app.engines.lsr.engine import lsr_engine
from app.engines.entities.engine import entity_engine

@pytest.mark.asyncio
async def test_sif_engine():
    # Energized equipment + negated LOTO should mean high SIF
    text = "worker exposed to energized equipment, loto not applied"
    res = await sif_engine.analyze(text)
    
    assert res["sif_potential"] is True
    assert res["risk_band"] == "HIGH"
    
    # Should find the evidence
    evidence_concepts = [e["concept"] for e in res["evidence"]]
    assert "ENERGIZED_EQUIPMENT" in evidence_concepts
    assert "LOTO" in evidence_concepts

@pytest.mark.asyncio
async def test_sif_negation():
    # Safely completed task should have low score
    text = "loto applied properly and verified before maintenance"
    res = await sif_engine.analyze(text)
    
    # "properly", "verified" lowers the weight
    assert res["sif_potential"] is False

@pytest.mark.asyncio
async def test_lsr_engine():
    text = "started maintenance but loto not applied"
    res = await lsr_engine.analyze(text)
    
    # Match ENERGY_ISOLATION
    assert len(res) >= 1
    codes = [r["rule_id"] for r in res]
    assert "ENERGY_ISOLATION" in codes

@pytest.mark.asyncio
async def test_entity_engine():
    text = "technician using a pump during maintenance"
    res = await entity_engine.extract(text)
    
    types = {r["entity_type"]: r["value"] for r in res}
    assert types.get("PERSON_ROLE") == "technician"
    assert types.get("EQUIPMENT") == "pump"
    assert types.get("ACTIVITY") == "maintenance"
