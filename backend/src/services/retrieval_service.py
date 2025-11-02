"""Semantic retrieval service."""

from __future__ import annotations

from collections.abc import Sequence

from backend.src.lib.embedding import embed_texts
from backend.src.models.entities import Section
from backend.src.pipelines.rerank import filter_low_relevance, rerank_sections
from backend.src.vector.faiss_index import VectorIndex
from sqlalchemy.orm import Session


class RetrievalService:
    def __init__(self, db: Session, vector_index: VectorIndex) -> None:
        self.db = db
        self.vector_index = vector_index

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        use_reranking: bool = True,
        min_relevance: float = 0.3,
    ) -> Sequence[Section]:
        """
        Retrieve and optionally re-rank sections for a query.
        
        Args:
            query: User query text
            top_k: Number of results to return
            use_reranking: Whether to apply re-ranking (default True)
            min_relevance: Minimum relevance score threshold (default 0.3)
            
        Returns:
            Sequence of relevant sections
        """
        embedding = embed_texts([query])
        # Fetch more candidates for re-ranking
        fetch_k = top_k * 2 if use_reranking else top_k
        matches = self.vector_index.search(embedding, k=fetch_k)
        
        if not matches:
            return []
        
        section_ids = [match[0] for match in matches]
        scores = [match[1] for match in matches]
        
        sections = (
            self.db.query(Section)
            .filter(Section.section_id.in_(section_ids))
            .all()
        )
        
        if not sections:
            return []
        
        # Maintain order from vector search
        id_to_section = {section.section_id: section for section in sections}
        ordered_sections = [
            id_to_section[sid] for sid in section_ids if sid in id_to_section
        ]
        ordered_scores = [
            score
            for sid, score in zip(section_ids, scores)
            if sid in id_to_section
        ]
        
        # Apply re-ranking if enabled
        if use_reranking:
            # Filter low relevance results
            filtered_sections, filtered_scores = filter_low_relevance(
                ordered_sections, ordered_scores, min_score=min_relevance
            )
            
            if not filtered_sections:
                return []
            
            # Re-rank with multiple heuristics
            return rerank_sections(
                filtered_sections,
                query,
                filtered_scores,
                top_k=top_k,
            )
        
        return ordered_sections[:top_k]
