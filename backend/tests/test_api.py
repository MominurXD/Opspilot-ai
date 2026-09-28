from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_shape():
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert {"metrics", "timeline", "forecast", "anomalies", "insights"} <= payload.keys()
    assert len(payload["forecast"]) == 7
