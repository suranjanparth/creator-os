from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_running_status() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "creator-os-api"}
