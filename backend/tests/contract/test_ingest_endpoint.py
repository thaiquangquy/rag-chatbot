import pytest
from fastapi.testclient import TestClient

from backend.src.api.main import app
from backend.src.api.routes import ingest as ingest_route


class DummyIngestService:
    def ingest(self, document_id: str, *, source_url: str) -> str:  # type: ignore[override]
        return "task-123"


def dependency_override():
    return DummyIngestService()


app.dependency_overrides[ingest_route.get_ingest_service] = dependency_override


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_ingest_returns_task_id(client):
    response = client.post("/ingest", json={"document_id": "abc", "source": "https://docs"})
    assert response.status_code == 202
    assert response.json() == {"task_id": "task-123"}
