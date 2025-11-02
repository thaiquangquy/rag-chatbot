from fastapi.testclient import TestClient

from backend.src.api.main import app
from backend.src.api.routes import chat as chat_route
from backend.src.services.answer_service import AnswerResult


class FakeRetrievalService:
    def retrieve(self, query: str, *, top_k: int = 5):
        class Section:
            def __init__(self, document_id: str, section_id: str, content: str):
                self.document_id = document_id
                self.section_id = section_id
                self.content = content
                self.document = type("Doc", (), {"url": "https://docs"})()

        return [Section("doc1", "sec1", "Answer content")]


class FakeAnswerService:
    def answer(self, question: str, sections: list[str]):
        return AnswerResult(
            response_id="resp-1",
            generated_text="Answer content",
            is_fallback=False,
        )


def override_retrieval():
    return FakeRetrievalService()


def override_answer():
    return FakeAnswerService()


app.dependency_overrides[chat_route.get_retrieval_service] = override_retrieval
app.dependency_overrides[chat_route.get_answer_service] = override_answer


def test_chat_returns_generated_text():
    client = TestClient(app)
    response = client.post("/chat", json={"query": "What is X?", "session_id": "sess-1"})
    assert response.status_code == 200
    body = response.json()
    assert body["response_id"] == "resp-1"
    assert body["generated_text"] == "Answer content"
    assert body["sources"]
    assert body["is_fallback"] is False
    assert body["related_topics"] == []
