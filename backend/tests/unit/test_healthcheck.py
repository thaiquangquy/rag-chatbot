from fastapi.testclient import TestClient

from backend.src.api.main import app


client = TestClient(app)


def test_healthcheck_returns_healthy_status() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
