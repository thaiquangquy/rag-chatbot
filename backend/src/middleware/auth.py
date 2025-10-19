"""Simple API key authentication middleware."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from backend.src.config.settings import get_settings


def api_key_guard(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    expected = settings.openai_api_key  # reuse for prototype; replace with dedicated key later
    if expected and x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    if not expected:
        # In local dev allow through but warn
        return
