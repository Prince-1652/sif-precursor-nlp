import pytest
from unittest.mock import patch
from app.services.processing import process_report
from app.models.report import Report
def test_process_report_success(db):
    report = Report(
        source="test_llm",
        source_record_id="llm_1",
        source_hash="hash_llm",
        report_type="UA",
        original_text="Oil spill in sector 7G",
        processing_status="READY",
        pipeline_version="1.0"
    )
    db.add(report)
    db.commit()
    report_id = str(report.id)
    
    with patch("app.services.processing.get_ai_provider") as mock_get_provider, \
         patch("app.services.processing.sif_engine") as mock_sif, \
         patch("app.services.processing.lsr_engine") as mock_lsr, \
         patch("app.services.processing.entity_engine") as mock_ent:
        
        from app.providers.mock import MockAIProvider
        from app.providers.base import NormalizationResult
        class TestMockProvider(MockAIProvider):
            async def normalize_text(self, text):
                return NormalizationResult(normalized_text=f"Normalized: {text}", language_detected="en", confidence=0.99)
            async def generate_embedding(self, text):
                return [0.5] * 768
        
        mock_get_provider.return_value = TestMockProvider()
        
        # AsyncMock for engines
        import asyncio
        async def mock_sif_analyze(text):
            return {
                "sif_potential": True, "score": 0.9, "confidence": 1.0,
                "risk_band": "HIGH", "engine": "test", "evidence": []
            }
        async def mock_lsr_analyze(text):
            return [{
                "rule_id": "ENERGY_ISOLATION", "score": 1.0, "confidence": 1.0,
                "matched_phrases": [], "method": "test"
            }]
        async def mock_ent_extract(text):
            return [{
                "entity_type": "HAZARD", "value": "Oil spill",
                "normalized_value": "Oil spill", "source_start": 0, "source_end": 5,
                "confidence": 1.0, "extraction_method": "test", "status": "UNKNOWN"
            }]
            
        mock_sif.analyze.side_effect = mock_sif_analyze
        mock_lsr.analyze.side_effect = mock_lsr_analyze
        mock_ent.extract.side_effect = mock_ent_extract
        
        process_report(report_id)
        
    # Since process_report uses its own session, we should use a fresh query or refresh
    db.expire_all()
    updated_report = db.query(Report).filter(Report.id == report_id).first()
    assert updated_report.processing_status in ["AUTO_ACCEPTED_HIGH_CONFIDENCE", "REVIEW_RECOMMENDED", "REVIEW_REQUIRED"]
    assert updated_report.sif_potential is True
    assert float(updated_report.sif_score) == 0.9
    assert updated_report.risk_band == "HIGH"
    
    from app.models.entity import Entity
    from app.models.sif_prediction import SIFPrediction
    
    entities = db.query(Entity).filter(Entity.report_id == report_id).all()
    assert len(entities) > 0
    hazards = [e.value for e in entities if e.entity_type == "HAZARD"]
    assert "Oil spill" in hazards
    
    sif_pred = db.query(SIFPrediction).filter(SIFPrediction.report_id == report_id).first()
    assert sif_pred is not None
    assert sif_pred.sif_potential is True
