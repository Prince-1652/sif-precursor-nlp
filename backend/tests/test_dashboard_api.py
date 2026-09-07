import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard_summary():
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_reports" in data
    assert "sif_percentage" in data

def test_dashboard_sites():
    response = client.get("/api/v1/dashboard/sites")
    assert response.status_code == 200
    data = response.json()
    assert "sites" in data

def test_dashboard_patterns():
    response = client.get("/api/v1/dashboard/patterns")
    assert response.status_code == 200
    data = response.json()
    assert "patterns" in data

def test_health_dependencies():
    response = client.get("/api/v1/health/dependencies")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "ok"
    
def test_reports_analyze():
    response = client.post("/api/v1/reports/analyze", json={"text": "A worker fell from a height and hit their head on the pavement. Energy isolation was missing."})
    assert response.status_code == 200
    data = response.json()
    assert "sif_result" in data
    assert "review_state" in data
