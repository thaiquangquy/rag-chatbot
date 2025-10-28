"""Contract test for chat endpoint with source attribution."""

import pytest
from backend.src.api.main import app
from backend.src.api.routes import chat as chat_route
from backend.src.models.entities import Document, Section
from fastapi.testclient import TestClient


class FakeRetrievalService:
    """Fake retrieval service for testing."""

    def __init__(self, sections=None):
        self.sections = sections or []

    def retrieve(self, query: str, *, top_k: int = 5):
        return self.sections


class FakeAnswerService:
    """Fake answer service for testing."""

    def answer(self, question: str, sections):
        return ("resp-123", "Test answer from sections.")


@pytest.fixture
def mock_section():
    """Create a mock section with document."""
    doc = Document(
        document_id="test_doc_1",
        title="Test Document",
        url="https://docs.google.com/document/d/test_doc_1/edit",
        mime_type="application/vnd.google-apps.document",
        owner="test@example.com",
        content_hash="abc123",
        ingestion_status="succeeded",
    )

    section = Section(
        section_id="section_1",
        document_id="test_doc_1",
        title="Introduction",
        content="This is a test section with relevant information about the company wiki.",
        char_offset_start=0,
        char_offset_end=100,
    )
    section.document = doc
    return section


def test_chat_response_includes_sources(mock_section):
    """Test that chat endpoint returns sources with URLs."""
    # Override dependencies
    app.dependency_overrides[chat_route.get_retrieval_service] = (
        lambda: FakeRetrievalService(sections=[mock_section])
    )
    app.dependency_overrides[chat_route.get_answer_service] = lambda: FakeAnswerService()

    try:
        client = TestClient(app)

        # Make request
        response = client.post(
            "/chat",
            json={"query": "What is in the wiki?", "session_id": "test_session"},
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "response_id" in data
        assert "generated_text" in data
        assert "sources" in data

        # Check sources
        assert len(data["sources"]) > 0
        source = data["sources"][0]

        # Verify source structure
        assert "document_id" in source
        assert "section_id" in source
        assert "snippet" in source
        assert "url" in source

        # Verify source content
        assert source["document_id"] == "test_doc_1"
        assert source["section_id"] == "section_1"
        assert len(source["snippet"]) > 0
        assert source["url"].startswith("https://docs.google.com/document/")
        assert "test_doc_1" in source["url"]
    finally:
        # Clear dependency overrides
        app.dependency_overrides.clear()


def test_chat_sources_are_clickable_urls(mock_section):
    """Test that source URLs are valid and clickable."""
    app.dependency_overrides[chat_route.get_retrieval_service] = (
        lambda: FakeRetrievalService(sections=[mock_section])
    )
    app.dependency_overrides[chat_route.get_answer_service] = lambda: FakeAnswerService()

    try:
        client = TestClient(app)
        response = client.post(
            "/chat",
            json={"query": "Test query", "session_id": "test_session"},
        )

        assert response.status_code == 200
        data = response.json()

        # Each source should have a valid URL
        for source in data["sources"]:
            url = source["url"]
            assert url.startswith("http://") or url.startswith("https://")
            assert len(url) > 0
    finally:
        app.dependency_overrides.clear()


def test_chat_multiple_sources(mock_section):
    """Test that multiple sources are returned when multiple sections match."""
    # Create a second mock section
    doc2 = Document(
        document_id="test_doc_2",
        title="Another Document",
        url="https://docs.google.com/document/d/test_doc_2/edit",
        mime_type="application/vnd.google-apps.document",
        owner="test@example.com",
        content_hash="def456",
        ingestion_status="succeeded",
    )

    section2 = Section(
        section_id="section_2",
        document_id="test_doc_2",
        title="Details",
        content="More relevant information from another document.",
        char_offset_start=0,
        char_offset_end=50,
    )
    section2.document = doc2

    app.dependency_overrides[chat_route.get_retrieval_service] = (
        lambda: FakeRetrievalService(sections=[mock_section, section2])
    )
    app.dependency_overrides[chat_route.get_answer_service] = lambda: FakeAnswerService()

    try:
        client = TestClient(app)
        response = client.post(
            "/chat",
            json={"query": "Complex query", "session_id": "test_session"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should have two sources
        assert len(data["sources"]) == 2

        # Verify both sources have proper structure
        for source in data["sources"]:
            assert "document_id" in source
            assert "section_id" in source
            assert "snippet" in source
            assert "url" in source
    finally:
        app.dependency_overrides.clear()
