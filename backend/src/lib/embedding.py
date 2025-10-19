"""Embedding helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def embed_texts(texts: Sequence[str]) -> np.ndarray:
    """Placeholder embedding generator using random vectors until provider wired."""
    rng = np.random.default_rng(seed=42)
    return rng.normal(size=(len(texts), 1536)).astype("float32")
