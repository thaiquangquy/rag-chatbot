"""Utilities for splitting documents into sections."""

from __future__ import annotations

from typing import Iterable


def chunk_text(text: str, max_tokens: int = 800) -> list[str]:
    """Naive chunker splitting by sentences."""
    sentences = text.split(". ")
    chunks: list[str] = []
    current: list[str] = []
    for sentence in sentences:
        proposed = current + [sentence]
        if sum(len(s) for s in proposed) > max_tokens and current:
            chunks.append(". ".join(current))
            current = [sentence]
        else:
            current = proposed
    if current:
        chunks.append(". ".join(current))
    return chunks
