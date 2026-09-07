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
    
    with patch("app.services.processing.get_ai_provider") as mock_get_provider:
        from app.services.ai_provider import MockAIProvider, SafetyAnalysisResult
        class TestMockProvider(MockAIProvider):
            async def analyze_safety(self, text):
                return SafetyAnalysisResult(
                    hazards=["Oil spill"],
                    root_causes=["Leaking valve"],
                    severity_score=4,
                    sif_potential=True,
                    sif_score=0.9,
                    risk_band="HIGH",
                    life_saving_rules=["Energy Isolation"],
                    precursors=["Failed valve"]
                )
            async def generate_embedding(self, text):
                return [0.5] * 768
        
        mock_get_provider.return_value = TestMockProvider()
        
        process_report(report_id)
        
    # Since process_report uses its own session, we should use a fresh query or refresh
    db.expire_all()
    updated_report = db.query(Report).filter(Report.id == report_id).first()
    
    assert updated_report.processing_status == "COMPLETED"
    assert updated_report.extracted_hazards == ["Oil spill"]
    assert updated_report.root_causes == ["Leaking valve"]
    assert updated_report.severity_score == 4
    assert len(updated_report.vector_embedding) == 768
    assert updated_report.ai_used is True
