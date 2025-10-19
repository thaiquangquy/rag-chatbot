"""Semantic retrieval service."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from sqlalchemy.orm import Session

from backend.src.lib.embedding import embed_texts
from backend.src.models.entities import Section
from backend.src.vector.faiss_index import VectorIndex


class RetrievalService:
    def __init__(self, db: Session, vector_index: VectorIndex) -> None:
        self.db = db
        self.vector_index = vector_index

    def retrieve(self, query: str, *, top_k: int = 5) -> Sequence[Section]:
        embedding = embed_texts([query])
        matches = self.vector_index.search(embedding, k=top_k)
        section_ids = [match[0] for match in matches]
        if not section_ids:
            return []
        return (
            self.db.query(Section)
            .filter(Section.section_id.in_(section_ids))
            .all()
        )
