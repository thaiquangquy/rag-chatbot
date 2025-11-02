"""Contract tests for fallback behaviour in /chat endpoint."""

import pytest
from fastapi.testclient import TestClient

from backend.src.api.main import app
from backend.src.api.routes import chat as chat_route
from backend.src.services.answer_service import AnswerService


class EmptyRetrievalService:
    """Retrieval service returning no sections."""

    def retrieve(self, query: str, *, top_k: int = 5):
        return []


class StubSuggestService:
    """Suggestion service returning deterministic topics."""

    def suggest_related_topics(self, question: str, limit: int = 3):
        return [
            "Credentials Overview",
            "Access Requests",
            "Support Contacts",
        ][:limit]

@pytest.fixture(autouse=True)
def override_dependencies():
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[chat_route.get_retrieval_service] = lambda: EmptyRetrievalService()
    app.dependency_overrides[chat_route.get_suggest_service] = lambda: StubSuggestService()
    app.dependency_overrides[chat_route.get_answer_service] = lambda: AnswerService()
    yield
    app.dependency_overrides = original_overrides


def test_chat_returns_fallback_with_related_topics():
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={"query": "How do I rotate credentials?", "session_id": "sess-fallback"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["is_fallback"] is True
    assert body["sources"] == []
    assert len(body["related_topics"]) == 3
    assert "credentials" in body["related_topics"][0].lower()
    assert "could" in body["generated_text"].lower() or "unable" in body["generated_text"].lower()


