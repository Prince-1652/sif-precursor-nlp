import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.models.report import Report
from app.main import app

def test_search_reports(client: TestClient, db):
    # Insert mock reports
    r1 = Report(
        source="test", report_type="UA", source_hash="hash1",
        original_text="Slip hazard", processing_status="COMPLETED",
        pipeline_version="1.0", vector_embedding=[0.1] * 768
    )
    r2 = Report(
        source="test", report_type="UA", source_hash="hash2",
        original_text="Fire hazard", processing_status="COMPLETED",
        pipeline_version="1.0", vector_embedding=[0.5] * 768
    )
    db.add_all([r1, r2])
    db.commit()

    with patch("app.api.endpoints.search.get_ai_provider") as mock_get_provider:
        from app.services.ai_provider import MockAIProvider
        class TestMockProvider(MockAIProvider):
            async def generate_embedding(self, text):
                return [0.1] * 768
        mock_get_provider.return_value = TestMockProvider()

        response = client.get("/api/v1/search?query=slip")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # r1 should be closer to query embedding [0.1]*768
        assert data[0]["original_text"] == "Slip hazard"
