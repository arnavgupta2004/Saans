from fastapi.testclient import TestClient

from app import app


def test_health_returns_versioned_success() -> None:
    response = TestClient(app).get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True, "version": "0.1.0"}
