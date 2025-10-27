"""Simplified FAISS index wrapper."""

from __future__ import annotations

from typing import Sequence

import faiss
import numpy as np


class VectorIndex:
    """Wrap FAISS index for cosine similarity search."""

    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.ids: list[str] = []
        self._embeddings: dict[str, np.ndarray] = {}

    def add(self, ids: Sequence[str], embeddings: np.ndarray) -> None:
        if embeddings.size == 0:
            return
        if embeddings.shape[1] != self.dimension:
            raise ValueError("Embedding dimension mismatch")
        normalized = np.ascontiguousarray(self._normalize(embeddings), dtype="float32")
        for vector_id, vector in zip(ids, normalized):
            self._embeddings[vector_id] = vector
        self._rebuild_index()

    def search(self, query: np.ndarray, k: int = 5) -> list[tuple[str, float]]:
        if query.shape[-1] != self.dimension:
            raise ValueError("Query dimension mismatch")
        if self.index.ntotal == 0:
            return []
        normalized_query = np.ascontiguousarray(self._normalize(query), dtype="float32")
        scores, indices = self.index.search(normalized_query, k)  # type: ignore[call-arg]
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
        return (embeddings / norms).astype("float32")

    def remove(self, ids: Sequence[str]) -> None:
        if not ids:
            return
        for vector_id in ids:
            self._embeddings.pop(vector_id, None)
        self._rebuild_index()

    def clear(self) -> None:
        self._embeddings.clear()
        self.index.reset()
        self.ids = []

    def _rebuild_index(self) -> None:
        self.index.reset()
        if not self._embeddings:
            self.ids = []
            return
        self.ids = list(self._embeddings.keys())
        matrix = np.stack([self._embeddings[idx] for idx in self.ids])
        self.index.add(np.ascontiguousarray(matrix, dtype="float32"))  # type: ignore[call-arg]
