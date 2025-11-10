"""Simplified FAISS index wrapper."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Sequence

import faiss
import numpy as np

DEFAULT_EMBEDDING_DIMENSION = 1536

class VectorIndex:
    """Wrap FAISS index for cosine similarity search."""

    def __init__(self, dimension: int = DEFAULT_EMBEDDING_DIMENSION) -> None:
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

    def save(self, path: str) -> None:
        """Save FAISS index and ID mapping to disk.
        
        Args:
            path: File path to save the index (e.g., 'data/faiss_index.bin')
        """
        # Create directory if it doesn't exist
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, path)
        
        # Save ID mapping and embeddings
        metadata_path = path + ".meta"
        metadata = {
            "ids": self.ids,
            "dimension": self.dimension,
            "embeddings": {
                key: value.tolist() for key, value in self._embeddings.items()
            }
        }
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

    def load(self, path: str) -> None:
        """Load FAISS index and ID mapping from disk.
        
        Args:
            path: File path to load the index from (e.g., 'data/faiss_index.bin')
        """
        if not os.path.exists(path):
            # If index doesn't exist, start with empty index
            return
        
        # Load FAISS index
        self.index = faiss.read_index(path)
        
        # Load ID mapping and embeddings
        metadata_path = path + ".meta"
        if not os.path.exists(metadata_path):
            # Fallback: if no metadata, reconstruct empty
            self.ids = []
            self._embeddings = {}
            return
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        self.ids = metadata.get("ids", [])
        self.dimension = metadata.get("dimension", self.dimension)
        
        # Reconstruct embeddings dict
        embeddings_dict = metadata.get("embeddings", {})
        self._embeddings = {
            key: np.array(value, dtype="float32")
            for key, value in embeddings_dict.items()
        }
