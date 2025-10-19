"""Combine retrieved sections into a response."""

from __future__ import annotations

import uuid

from backend.src.providers.llm_provider import ChatProvider, StubProvider


class AnswerService:
    def __init__(self, provider: ChatProvider | None = None) -> None:
        self.provider = provider or StubProvider()

    def answer(self, question: str, sections: list[str]) -> tuple[str, str]:
        context = "\n".join(sections)
        prompt = f"CONTEXT:\n{context}\n\nQUESTION: {question}\nANSWER:"
        generated = self.provider.generate(prompt)
        return str(uuid.uuid4()), generated
