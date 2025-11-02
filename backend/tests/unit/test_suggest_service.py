"""Unit tests for related topic suggestion service."""

from backend.src.services.suggest_service import SuggestService


def test_suggest_service_returns_keywords():
    service = SuggestService()
    suggestions = service.suggest_related_topics("How do I set up single sign-on?", limit=2)

    assert len(suggestions) == 2
    assert any("Single" in suggestion for suggestion in suggestions)


def test_suggest_service_defaults_when_no_keywords():
    service = SuggestService()
    suggestions = service.suggest_related_topics("What is it?", limit=3)

    assert len(suggestions) == 3
    assert "documentation" in suggestions[0].lower() or "support" in suggestions[0].lower()
