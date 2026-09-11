import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.services.processing import process_pending_reports_async
from app.models.report import Report
from app.engines.language_gate.gate import LanguageGateDecision

# A mock for the Language Detector to force reports into the Non-English path
class MockLanguageDetector:
    class MockDetection:
        language_code = "es"
        confidence = 0.9
        is_mixed = False
    def detect(self, text):
        return self.MockDetection()

@pytest.fixture(autouse=True)
def clear_db(db):
    db.query(Report).delete()
    db.commit()

@pytest.fixture
def non_english_reports(db):
    reports = []
    for i in range(12):  # 12 reports = 2 full batches of 5, plus a partial batch of 2
        report = Report(
            source="stress_test",
            source_record_id=f"rec_{i}",
            source_hash=f"hash_{i}",
            report_type="UA",
            original_text=f"Test report {i} in Spanish",
            processing_status="READY",
            pipeline_version="1.0"
        )
        db.add(report)
        reports.append(report)
    db.commit()
    return reports

@pytest.mark.asyncio
@patch("app.services.processing.process_report_async")
@patch("app.engines.language_gate.detector.LanguageDetector", return_value=MockLanguageDetector())
@patch("app.engines.language_gate.gate.decide_routing", return_value=LanguageGateDecision.AI_NORMALIZATION)
async def test_consecutive_failures_reset(mock_routing, mock_detector, mock_process, db, non_english_reports):
    """
    Test that failures reset when a success occurs.
    Batch 1 (indices 0-4): Fail, Fail, Success, Fail, Fail. (Max 2 consecutive).
    Batch 2 (indices 5-9): Success, Fail, Success, Fail, Fail. (Max 2 consecutive).
    Batch 3 (indices 10-11): Success, Success.
    Circuit breaker should NEVER trip.
    Failed ones should go to DLQ. Passed ones should NOT go to DLQ.
    """
    # 0=fail, 1=fail, 2=pass, 3=fail, 4=fail
    # 5=pass, 6=fail, 7=pass, 8=fail, 9=fail
    # 10=pass, 11=pass
    failed_indices = {0, 1, 3, 4, 6, 8, 9}
    
    async def mock_process_side_effect(rid):
        idx = next(i for i, r in enumerate(non_english_reports) if str(r.id) == str(rid))
        if idx in failed_indices:
            return False # Failure
        return True # Success

    mock_process.side_effect = mock_process_side_effect

    await process_pending_reports_async()
    
    db.expire_all()
    
    # Check DLQ counts. Exactly the failed_indices should be in DLQ.
    reports_in_dlq = db.query(Report).filter(Report.processing_status == "DLQ").all()
    assert len(reports_in_dlq) == len(failed_indices)
    
    dlq_ids = [r.id for r in reports_in_dlq]
    for idx in failed_indices:
        assert non_english_reports[idx].id in dlq_ids

@pytest.mark.asyncio
@patch("app.services.processing.process_report_async")
@patch("app.engines.language_gate.detector.LanguageDetector", return_value=MockLanguageDetector())
@patch("app.engines.language_gate.gate.decide_routing", return_value=LanguageGateDecision.AI_NORMALIZATION)
async def test_circuit_breaker_trips_cross_batch(mock_routing, mock_detector, mock_process, db, non_english_reports):
    """
    Test that the circuit breaker trips when 3 consecutive failures span across batches.
    Batch 1 (indices 0-4): Pass, Pass, Pass, Fail, Fail.
    Batch 2 (indices 5-9): Fail, ... (Should trip immediately on index 5)
    The remaining untouched reports (indices 6-11) should go to DLQ.
    The failed ones (3, 4, 5) should also go to DLQ.
    """
    async def mock_process_side_effect(rid):
        idx = next(i for i, r in enumerate(non_english_reports) if str(r.id) == str(rid))
        if idx in [3, 4, 5]:
            return False
        return True

    mock_process.side_effect = mock_process_side_effect

    await process_pending_reports_async()
    
    db.expire_all()
    
    # Batch 1 failed ones: 3, 4 -> should be DLQ
    # Batch 2: processing index 5 caused trip. So 5 is a failed one in current batch -> DLQ.
    # Because breaker tripped during Batch 2, remaining ids (from 6 to 11) -> DLQ.
    reports_in_dlq = db.query(Report).filter(Report.processing_status == "DLQ").all()
    
    # Expected DLQ: 3, 4, 5 (failed) + 6, 7, 8, 9, 10, 11 (unattempted future) = 9 reports
    assert len(reports_in_dlq) == 9
    
    # Indices 0, 1, 2 were successes, should NOT be in DLQ.
    dlq_indices = [next(i for i, rep in enumerate(non_english_reports) if str(rep.id) == str(r.id)) for r in reports_in_dlq]
    assert 0 not in dlq_indices
    assert 1 not in dlq_indices
    assert 2 not in dlq_indices
    assert 3 in dlq_indices
    assert 4 in dlq_indices
    assert 5 in dlq_indices
    assert 6 in dlq_indices
    assert 11 in dlq_indices

@pytest.mark.asyncio
@patch("app.services.processing.process_report_async")
@patch("app.engines.language_gate.detector.LanguageDetector", return_value=MockLanguageDetector())
@patch("app.engines.language_gate.gate.decide_routing", return_value=LanguageGateDecision.AI_NORMALIZATION)
async def test_immediate_trip(mock_routing, mock_detector, mock_process, db, non_english_reports):
    """
    Test that if the first 3 fail, it trips immediately in Batch 1.
    Indices 0, 1, 2 fail.
    The remaining unattempted (indices 3-11) go to DLQ.
    The failed (0, 1, 2) go to DLQ.
    Everything is DLQ!
    """
    async def mock_process_side_effect(rid):
        idx = next(i for i, r in enumerate(non_english_reports) if str(r.id) == str(rid))
        if idx in [0, 1, 2]:
            return Exception("API Timeout")
        return True

    mock_process.side_effect = mock_process_side_effect

    await process_pending_reports_async()
    
    db.expire_all()
    
    reports_in_dlq = db.query(Report).filter(Report.processing_status == "DLQ").all()
    assert len(reports_in_dlq) == 12 # All 12 should be DLQ'd
