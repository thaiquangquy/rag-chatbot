"""Unit tests for relevance scoring and re-ranking."""

from __future__ import annotations

from typing import cast

from backend.src.models.entities import Section
from backend.src.pipelines.rerank import (
    ScoredSection,
    compute_diversity_score,
    compute_keyword_score,
    filter_low_relevance,
    rerank_sections,
)
from backend.src.services.answer_service import AnswerService


class TestKeywordScore:
    """Tests for keyword scoring."""

    def test_perfect_match(self) -> None:
        """Test keyword score with perfect query match."""
        score = compute_keyword_score("python programming language", "python programming")
        assert score == 1.0

    def test_partial_match(self) -> None:
        """Test keyword score with partial match."""
        score = compute_keyword_score("python programming language tutorial", "python language")
        assert score == 1.0  # Both query terms present

    def test_no_match(self) -> None:
        """Test keyword score with no match."""
        score = compute_keyword_score("javascript tutorial", "python programming")
        assert score == 0.0

    def test_case_insensitive(self) -> None:
        """Test that keyword scoring is case-insensitive."""
        score = compute_keyword_score("Python Programming Language", "PYTHON programming")
        assert score == 1.0

    def test_empty_query(self) -> None:
        """Test keyword score with empty query."""
        score = compute_keyword_score("some content", "")
        assert score == 0.0


class TestDiversityScore:
    """Tests for diversity scoring."""

    def test_first_result_max_diversity(self) -> None:
        """First result should have maximum diversity."""
        score = compute_diversity_score("python programming", [])
        assert score == 1.0

    def test_duplicate_content_low_diversity(self) -> None:
        """Duplicate content should have low diversity."""
        content = "python programming language"
        score = compute_diversity_score(content, [content])
        assert score < 0.5

    def test_different_content_high_diversity(self) -> None:
        """Different content should have high diversity."""
        score = compute_diversity_score(
            "javascript web development",
            ["python data science", "java enterprise applications"]
        )
        assert score > 0.5

    def test_partial_overlap_medium_diversity(self) -> None:
        """Partial overlap should result in medium diversity."""
        score = compute_diversity_score(
            "python web development",
            ["python data science"]
        )
        assert 0.3 < score < 0.8


class TestScoredSection:
    """Tests for ScoredSection class."""

    def test_initial_score(self) -> None:
        """Test initial score is set to semantic score."""
        section = Section(
            section_id="s1",
            document_id="d1",
            content="test content",
        )
        scored = ScoredSection(section, 0.8)
        assert scored.semantic_score == 0.8
        assert scored.final_score == 0.8

    def test_compute_final_score_default_weights(self) -> None:
        """Test final score computation with default weights."""
        section = Section(
            section_id="s1",
            document_id="d1",
            content="test content",
        )
        scored = ScoredSection(section, 0.8)
        scored.keyword_score = 0.6
        scored.diversity_score = 0.9
        scored.compute_final_score()
        
        expected = 0.7 * 0.8 + 0.2 * 0.6 + 0.1 * 0.9
        assert abs(scored.final_score - expected) < 0.001

    def test_compute_final_score_custom_weights(self) -> None:
        """Test final score computation with custom weights."""
        section = Section(
            section_id="s1",
            document_id="d1",
            content="test content",
        )
        scored = ScoredSection(section, 0.8)
        scored.keyword_score = 0.6
        scored.diversity_score = 0.9
        scored.compute_final_score(semantic_weight=0.5, keyword_weight=0.3, diversity_weight=0.2)
        
        expected = 0.5 * 0.8 + 0.3 * 0.6 + 0.2 * 0.9
        assert abs(scored.final_score - expected) < 0.001


class TestRerankSections:
    """Tests for re-ranking functionality."""

    def test_empty_sections(self) -> None:
        """Test re-ranking with empty section list."""
        result = rerank_sections([], "test query", [])
        assert result == []

    def test_single_section(self) -> None:
        """Test re-ranking with single section."""
        section = Section(
            section_id="s1",
            document_id="d1",
            content="python programming",
        )
        result = rerank_sections([section], "python", [0.8])
        assert len(result) == 1
        assert cast(str, result[0].section_id) == "s1"

    def test_rerank_by_keyword_boost(self) -> None:
        """Test that keyword matching boosts rankings."""
        s1 = Section(section_id="s1", document_id="d1", content="python programming language")
        s2 = Section(section_id="s2", document_id="d1", content="java development tools")
        
        # s2 has higher semantic score but s1 matches query better
        result = rerank_sections(
            [s1, s2],
            "python programming",
            [0.6, 0.7],  # s2 has higher semantic score
            semantic_weight=0.5,
            keyword_weight=0.5,
            diversity_weight=0.0,
        )
        
        # s1 should rank higher due to keyword match
        assert cast(str, result[0].section_id) == "s1"

    def test_top_k_limit(self) -> None:
        """Test that top_k limits results."""
        sections = [
            Section(section_id=f"s{i}", document_id="d1", content=f"content {i}")
            for i in range(10)
        ]
        scores = [0.9 - i * 0.05 for i in range(10)]
        
        result = rerank_sections(sections, "test", scores, top_k=3)
        assert len(result) == 3


class TestFilterLowRelevance:
    """Tests for relevance filtering."""

    def test_all_above_threshold(self) -> None:
        """Test filtering when all sections are above threshold."""
        sections = [
            Section(section_id="s1", document_id="d1", content="content 1"),
            Section(section_id="s2", document_id="d1", content="content 2"),
        ]
        scores = [0.8, 0.7]
        
        filtered_sections, filtered_scores = filter_low_relevance(sections, scores, min_score=0.5)
        assert len(filtered_sections) == 2
        assert len(filtered_scores) == 2

    def test_some_below_threshold(self) -> None:
        """Test filtering when some sections are below threshold."""
        sections = [
            Section(section_id="s1", document_id="d1", content="content 1"),
            Section(section_id="s2", document_id="d1", content="content 2"),
            Section(section_id="s3", document_id="d1", content="content 3"),
        ]
        scores = [0.8, 0.4, 0.6]
        
        filtered_sections, filtered_scores = filter_low_relevance(sections, scores, min_score=0.5)
        assert len(filtered_sections) == 2
        assert cast(str, filtered_sections[0].section_id) == "s1"
        assert cast(str, filtered_sections[1].section_id) == "s3"
        assert filtered_scores == [0.8, 0.6]

    def test_all_below_threshold(self) -> None:
        """Test filtering when all sections are below threshold."""
        sections = [
            Section(section_id="s1", document_id="d1", content="content 1"),
            Section(section_id="s2", document_id="d1", content="content 2"),
        ]
        scores = [0.3, 0.2]
        
        filtered_sections, filtered_scores = filter_low_relevance(sections, scores, min_score=0.5)
        assert len(filtered_sections) == 0
        assert len(filtered_scores) == 0


class TestAmbiguityDetection:
    """Tests for ambiguity detection in answer service."""

    def test_short_query_is_ambiguous(self) -> None:
        """Test that very short queries are detected as ambiguous."""
        service = AnswerService()
        assert service.is_ambiguous("how")
        assert service.is_ambiguous("what is")

    def test_vague_short_query_is_ambiguous(self) -> None:
        """Test that vague short queries are ambiguous."""
        service = AnswerService()
        assert service.is_ambiguous("tell me about")
        assert service.is_ambiguous("explain that")

    def test_specific_query_not_ambiguous(self) -> None:
        """Test that specific queries are not ambiguous."""
        service = AnswerService()
        assert not service.is_ambiguous("how do I reset my password in the admin portal")
        assert not service.is_ambiguous("what is the API endpoint for user authentication")

    def test_medium_length_specific_not_ambiguous(self) -> None:
        """Test that medium-length specific queries are not ambiguous."""
        service = AnswerService()
        assert not service.is_ambiguous("python error handling best practices")

    def test_generate_clarifying_prompt(self) -> None:
        """Test that clarifying prompt is generated properly."""
        service = AnswerService()
        prompt = service.generate_clarifying_prompt("what")
        assert "what" in prompt.lower()
        assert "details" in prompt.lower() or "context" in prompt.lower()

    def test_ambiguous_query_with_no_sections_returns_clarification(self) -> None:
        """Test that ambiguous queries with no context get clarification."""
        service = AnswerService()
        result = service.answer("what", [])
        assert "details" in result.generated_text.lower() or "clarif" in result.generated_text.lower()
        assert result.is_fallback is False

    def test_specific_query_generates_normal_answer(self) -> None:
        """Test that specific queries generate normal answers."""
        service = AnswerService()
        result = service.answer(
            "how do I reset my password",
            [
                "You can reset your password in the settings page. Navigate to the security tab "
                "and follow the on-screen prompts to confirm the change."
            ]
        )
        # Should not be a clarifying prompt
        assert "could you please provide more details" not in result.generated_text.lower()
        assert result.is_fallback is False


class TestFallbackPolicy:
    """Tests for fallback behaviour in AnswerService."""

    def test_no_sections_triggers_fallback(self) -> None:
        """Ensure fallback is returned when no context is available."""
        service = AnswerService()
        result = service.answer("Explain upstream latency budget", [])
        assert result.is_fallback is True
        assert "couldn't find" in result.generated_text.lower() or "no relevant" in result.generated_text.lower()

    def test_short_context_triggers_fallback(self) -> None:
        """Short responses should trigger fallback message."""
        service = AnswerService(min_context_chars=50)
        context = ["tiny"]
        result = service.answer("Explain upstream latency budget", context)
        assert result.is_fallback is True
        assert len(result.generated_text) > 0
