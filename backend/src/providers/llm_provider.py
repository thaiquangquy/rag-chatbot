"""LLM provider abstraction supporting OpenAI and Ollama."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ChatProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        raise NotImplementedError


class StubProvider(ChatProvider):
    def generate(self, prompt: str, *, temperature: float = 0.2) -> str:
        return "Stub response: " + prompt[:100]
