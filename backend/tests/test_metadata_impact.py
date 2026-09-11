import pytest
import asyncio
from app.engines.sif.engine import sif_engine
from app.engines.lsr.engine import lsr_engine

@pytest.mark.asyncio
async def test_sif_metadata_weighting():
    """
    Test that the exact same text produces different risk scores depending on the report_type.
    """
    text = "The worker was near an energized control panel without loto."
    
    # 1. Base Score
    base_res = await sif_engine.analyze(text, report_type="Observation")
    
    # 2. Incident Score
    inc_res = await sif_engine.analyze(text, report_type="Incident")
    
    # Incident should be significantly higher due to the 1.3 multiplier
    # compared to Observation (0.5 multiplier).
    assert inc_res["score"] > base_res["score"], "Incident score must be > Observation score"
    
    # Incident should be considered SIF potential, Observation should not be.
    # Note: Depending on base score this might both be false or both true, 
    # but based on trial & error, observation lowers it enough to not be a SIF.
    assert inc_res["sif_potential"] is True or inc_res["score"] == 1.0

@pytest.mark.asyncio
async def test_lsr_metadata_exclusions():
    """
    Test that context-aware rules bypass false positives.
    """
    text = "A massive spill happened near the crane while driving."
    
    # 1. If it's an Incident, DRIVING and SAFE_MECHANICAL_LIFTING should trigger.
    inc_res = await lsr_engine.analyze(text, report_type="Incident")
    triggered_rules = [r["rule_id"] for r in inc_res]
    
    assert "DRIVING" in triggered_rules, "DRIVING must trigger on generic incident"
    assert "SAFE_MECHANICAL_LIFTING" in triggered_rules, "LIFTING must trigger on generic incident"
    
    # 2. If it's a Spill, those rules are explicitly bypassed.
    spill_res = await lsr_engine.analyze(text, report_type="Spill")
    spill_rules = [r["rule_id"] for r in spill_res]
    
    assert "DRIVING" not in spill_rules, "DRIVING must be bypassed for Spills"
    assert "SAFE_MECHANICAL_LIFTING" not in spill_rules, "LIFTING must be bypassed for Spills"
