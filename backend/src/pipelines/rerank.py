"""Re-ranking heuristics for retrieved sections."""

from __future__ import annotations

from collections.abc import Sequence

from backend.src.models.entities import Section


class ScoredSection:
    """A section with combined relevance scores."""

    def __init__(self, section: Section, semantic_score: float) -> None:
        self.section = section
        self.semantic_score = semantic_score
        self.keyword_score = 0.0
        self.diversity_score = 0.0
        self.final_score = semantic_score

    def compute_final_score(
        self,
        *,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.2,
        diversity_weight: float = 0.1,
    ) -> None:
        """Compute weighted final score from component scores."""
        self.final_score = (
            semantic_weight * self.semantic_score
            + keyword_weight * self.keyword_score
            + diversity_weight * self.diversity_score
        )


def compute_keyword_score(section_content: str, query: str) -> float:
    """
    Calculate keyword overlap score between query and section.
    
    Returns a score in [0, 1] based on term overlap.
    """
    query_terms = set(query.lower().split())
    section_terms = set(section_content.lower().split())
    
    if not query_terms:
        return 0.0
    
    overlap = len(query_terms & section_terms)
    return overlap / len(query_terms)


def compute_diversity_score(section_content: str, already_selected: list[str]) -> float:
    """
    Calculate diversity score to avoid redundant results.
    
    Returns a score in [0, 1] where higher means more diverse.
    """
    if not already_selected:
        return 1.0
    
    section_terms = set(section_content.lower().split())
    
    # Calculate average term overlap with already selected sections
    overlaps = []
    for selected_content in already_selected:
        selected_terms = set(selected_content.lower().split())
        if not section_terms or not selected_terms:
            overlaps.append(0.0)
        else:
            overlap = len(section_terms & selected_terms)
            overlaps.append(overlap / max(len(section_terms), len(selected_terms)))
    
    # Higher diversity when overlap is lower
    avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0.0
    return 1.0 - avg_overlap


def rerank_sections(
    sections: Sequence[Section],
    query: str,
    semantic_scores: Sequence[float],
    *,
    top_k: int = 5,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.2,
    diversity_weight: float = 0.1,
) -> list[Section]:
    """
    Re-rank retrieved sections using multiple scoring heuristics.
    
    Args:
        sections: Retrieved sections from vector search
        query: User query text
        semantic_scores: Cosine similarity scores from vector search
        top_k: Number of results to return
        semantic_weight: Weight for semantic similarity score
        keyword_weight: Weight for keyword overlap score
        diversity_weight: Weight for diversity score
    
    Returns:
        Re-ranked list of sections (top_k items)
    """
    if not sections:
        return []
    
    # Create scored sections with semantic scores
    scored_sections = [
        ScoredSection(section, score)
        for section, score in zip(sections, semantic_scores)
    ]
    
    # Compute keyword scores
    for scored in scored_sections:
        scored.keyword_score = compute_keyword_score(scored.section.content, query)
    
    # Compute diversity scores progressively
    selected_contents: list[str] = []
    for scored in scored_sections:
        scored.diversity_score = compute_diversity_score(scored.section.content, selected_contents)
        scored.compute_final_score(
            semantic_weight=semantic_weight,
            keyword_weight=keyword_weight,
            diversity_weight=diversity_weight,
        )
        selected_contents.append(scored.section.content)
    
    # Sort by final score and return top_k
    scored_sections.sort(key=lambda x: x.final_score, reverse=True)
    return [scored.section for scored in scored_sections[:top_k]]


def filter_low_relevance(
    sections: Sequence[Section],
    semantic_scores: Sequence[float],
    *,
    min_score: float = 0.5,
) -> tuple[list[Section], list[float]]:
    """
    Filter out sections with semantic score below threshold.
    
    Args:
        sections: Retrieved sections
        semantic_scores: Corresponding semantic similarity scores
        min_score: Minimum acceptable score (0 to 1)
    
    Returns:
        Tuple of (filtered_sections, filtered_scores)
    """
    filtered = [
        (section, score)
        for section, score in zip(sections, semantic_scores)
        if score >= min_score
    ]
    
    if not filtered:
        return [], []
    
    filtered_sections, filtered_scores = zip(*filtered)
    return list(filtered_sections), list(filtered_scores)
