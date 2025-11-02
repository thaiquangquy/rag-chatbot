"""Generate related topic suggestions for fallback responses."""

from __future__ import annotations

import re
from typing import Iterable, Sequence

_DEFAULT_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "for",
    "with",
    "this",
    "that",
    "these",
    "those",
    "what",
    "when",
    "where",
    "why",
    "how",
    "who",
    "which",
    "are",
    "was",
    "were",
    "been",
    "being",
    "have",
    "has",
    "had",
    "can",
    "could",
    "should",
    "would",
    "do",
    "does",
    "did",
    "into",
    "from",
    "about",
    "your",
    "their",
    "our",
    "please",
    "set",
    "setup",
    "up",
}


class SuggestService:
    """Simple keyword-based related topic suggester."""

    def __init__(self, *, stopwords: Iterable[str] | None = None) -> None:
        self.stopwords = set(_DEFAULT_STOPWORDS)
        if stopwords:
            self.stopwords.update(token.lower() for token in stopwords)

    def suggest_related_topics(self, question: str, limit: int = 3) -> list[str]:
        """Generate a list of related topics based on query keywords."""

        raw_keywords = self._extract_keywords(question)
        ordered_keywords: list[str] = []
        seen_keywords: set[str] = set()
        for keyword in raw_keywords:
            if keyword not in seen_keywords:
                ordered_keywords.append(keyword)
                seen_keywords.add(keyword)

        phrase_candidates = self._combine_adjacent_keywords(raw_keywords)
        candidates = phrase_candidates + ordered_keywords

        suggestions: list[str] = []

        for keyword in candidates:
            title = keyword.title()
            for suffix in ("Overview", "Best Practices", "Troubleshooting"):
                suggestion = f"{title} {suffix}"
                if suggestion not in suggestions:
                    suggestions.append(suggestion)
                if len(suggestions) >= limit:
                    break
            if len(suggestions) >= limit:
                break

        if not suggestions:
            fallback = [
                "Review Onboarding Documentation",
                "Contact Support Team",
                "Search The Wiki",
            ]
            return fallback[:limit]

        return suggestions[:limit]

    def _extract_keywords(self, question: str) -> Sequence[str]:
        """Tokenize question and remove stopwords and short tokens."""

        tokens = re.findall(r"[a-zA-Z0-9]+", question.lower())
        keywords: list[str] = []
        for token in tokens:
            if len(token) < 3:
                continue
            if token in self.stopwords:
                continue
            keywords.append(token)
        return keywords

    def _combine_adjacent_keywords(self, keywords: Sequence[str]) -> list[str]:
        """Combine adjacent keywords into phrase candidates."""

        phrases: list[str] = []
        for first, second in zip(keywords, keywords[1:]):
            if first in self.stopwords or second in self.stopwords:
                continue
            phrase = f"{first} {second}"
            if phrase not in phrases:
                phrases.append(phrase)
        return phrases
