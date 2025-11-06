"""Embedding helpers."""

from __future__ import annotations

from typing import Sequence

import httpx
import numpy as np

from backend.src.config.settings import get_settings


def embed_texts(texts: Sequence[str]) -> np.ndarray:
    """Generate embeddings for text sequences using the configured provider."""
    settings = get_settings()
    dimension = settings.embedding_dimension
    if not texts:
        return np.empty((0, dimension), dtype="float32")

    provider = settings.embedding_provider.lower()
    if provider == "lm_studio":
        base_url = settings.lm_studio_base_url.rstrip("/")
        endpoint = f"{base_url}/embeddings"
        payload = {"input": list(texts), "model": settings.lm_studio_embedding_model}
        try:
            response = httpx.post(endpoint, json=payload, timeout=settings.lm_studio_timeout_seconds)
        except httpx.HTTPError as exc:  # pragma: no cover - network failure path
            raise RuntimeError("Failed to call LM Studio embeddings endpoint") from exc

        if response.status_code >= 400:
            raise RuntimeError(
                "LM Studio embeddings request failed: "
                f"{response.status_code} {response.text.strip()}"
            )

        try:
            data = response.json()
            vectors = [np.asarray(item["embedding"], dtype="float32") for item in data["data"]]
        except (KeyError, TypeError, ValueError) as exc:  # pragma: no cover - malformed payload
            raise RuntimeError("Unexpected response structure from LM Studio embeddings API") from exc

        if not vectors:
            return np.empty((0, dimension), dtype="float32")

        embeddings = np.stack(vectors)
        if embeddings.shape[1] != dimension:
            raise ValueError(
                "Embedding dimension mismatch between LM Studio response "
                f"({embeddings.shape[1]}) and configured embedding_dimension ({dimension})."
            )
        return embeddings

    rng = np.random.default_rng()
    return rng.normal(size=(len(texts), dimension)).astype("float32")
