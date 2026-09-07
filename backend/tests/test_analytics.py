import pytest
from app.engines.analytics import compute_summary, compute_site_density, mine_patterns

def test_compute_summary(db):
    summary = compute_summary(db)
    assert "total_reports" in summary
    assert "sif_count" in summary
    assert "sif_percentage" in summary
    assert "high_risk_count" in summary
    assert "review_count" in summary
    assert "lsr_distribution" in summary
    assert "generated_at" in summary

def test_compute_site_density(db):
    densities = compute_site_density(db)
    assert isinstance(densities, list)
    # The DB is likely empty from the fixture so densities might be empty, but that's fine

def test_mine_patterns(db):
    patterns = mine_patterns(db)
    assert isinstance(patterns, list)
