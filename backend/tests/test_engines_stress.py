import pytest
import asyncio
from app.engines.sif.engine import sif_engine
from app.engines.lsr.matcher import LSRMatcher
from app.engines.lsr.rule_loader import LSRRuleDef
from app.engines.entities.engine import entity_engine

@pytest.mark.asyncio
async def test_sif_word_boundary_slicing_bug():
    """
    Test the 'sliced word' bug where a 30-character context window 
    might slice the word 'cannot' into 'not', causing a false positive negation.
    """
    # The keyword is 'fatality', which triggers a hazard rule.
    # We place the word 'knot' exactly 28 characters before the match so
    # start-30 cuts it into 'not'.
    # e.g., "...k" (cut) "not prevent the fatality..."
    # If the slicing bug exists, it will see 'not', applying negation multiplier.
    # With token-aware slicing, it should see 'knot' and NOT apply 'not' negation multiplier.
    
    text = "The worker tied a secure knot to prevent the fatality from occurring."
    # If it falsely matches 'not', the weight for OUTCOME drops to 0.2 (from 1.0)
    # If it works correctly, the weight remains 1.0.
    result = await sif_engine.analyze(text)
    
    evidence = [e for e in result["evidence"] if e["text"] == "fatality"]
    assert len(evidence) > 0, "Should extract 'fatality'"
    
    # In sif/negation.py, OUTCOME with 'not' gets 0.2.
    # With 'knot', it should NOT match 'not' because of word boundaries, so weight should be 1.0.
    assert evidence[0]["weight"] == 1.0, f"Weight should be 1.0, got {evidence[0]['weight']}. Slicing bug detected!"

@pytest.mark.asyncio
async def test_entities_substring_match_bug():
    """
    Test the 'substring match' bug where `any(w in context)` 
    matches 'not' inside 'notice' or 'nothing'.
    """
    # Barrier keyword: 'harness'
    # Context word: 'notice' (contains 'not', 'no')
    # If substring bug exists, barrier status becomes FAILED.
    # With exact word boundaries, it should be UNKNOWN or SUCCESSFUL.
    
    text = "I did notice that the worker was wearing a harness perfectly."
    
    entities = await entity_engine.extract(text)
    harness_entities = [e for e in entities if e["value"] == "harness"]
    
    assert len(harness_entities) > 0, "Should extract 'harness'"
    # Because of 'perfectly'/'notice', if the bug exists, 'not' in 'notice' 
    # triggers FAILED before 'perfectly' triggers anything (or vice versa).
    assert harness_entities[0]["status"] != "FAILED", "Substring match bug detected! 'notice' triggered 'not'/'no'."

@pytest.mark.asyncio
async def test_entities_deduplication_data_loss():
    """
    Test that deduplication groups occurrences instead of throwing them away.
    """
    # We mention 'spill' twice in the report.
    text = "There was a spill at the start. Another spill happened later."
    
    entities = await entity_engine.extract(text)
    spill_entities = [e for e in entities if e["value"] == "spill"]
    
    assert len(spill_entities) == 1, "Entities should be grouped by type/value"
    assert "occurrences" in spill_entities[0], "Entity should have 'occurrences' list"
    assert len(spill_entities[0]["occurrences"]) == 2, "Data loss bug! Both occurrences should be preserved."

@pytest.mark.asyncio
async def test_stress_long_report():
    """
    Stress test with an artificially massive report.
    """
    # 10,000 words.
    base_text = "The worker was wearing a harness but there was a spill hazard. "
    massive_text = base_text * 1000  # ~10,000+ words
    
    # Should not crash or hang.
    result = await sif_engine.analyze(massive_text)
    
    entities = await entity_engine.extract(massive_text)
    assert len(entities) > 0
    
    # Check deduplication on massive scale
    spill_entities = [e for e in entities if e["value"] == "spill"]
    assert len(spill_entities[0]["occurrences"]) == 1000

