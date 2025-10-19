"""Simplified FAISS index wrapper."""

from __future__ import annotations

from typing import Iterable, Sequence

import faiss
import numpy as np


class VectorIndex:
    """Wrap FAISS index for cosine similarity search."""

    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.ids: list[str] = []

    def add(self, ids: Sequence[str], embeddings: np.ndarray) -> None:
        if embeddings.shape[1] != self.dimension:
            raise ValueError("Embedding dimension mismatch")
        normalized = self._normalize(embeddings)
        self.index.add(normalized)
        self.ids.extend(ids)

    def search(self, query: np.ndarray, k: int = 5) -> list[tuple[str, float]]:
        if query.shape[-1] != self.dimension:
            raise ValueError("Query dimension mismatch")
        normalized_query = self._normalize(query)
        scores, indices = self.index.search(normalized_query, k)
        results: list[tuple[str, float]] = []
        for row_scores, row_indices in zip(scores, indices):
            for score, idx in zip(row_scores, row_indices):
                if idx == -1:
                    continue
                results.append((self.ids[idx], float(score)))
        return results

    @staticmethod
    def _normalize(embeddings: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return embeddings / norms
