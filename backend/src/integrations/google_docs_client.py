"""Google Docs API client abstraction."""

from __future__ import annotations

from typing import Any


class GoogleDocsClient:
    def __init__(self, credentials_path: str | None = None) -> None:
        self.credentials_path = credentials_path

    def fetch_document(self, document_id: str) -> dict[str, Any]:
        """Placeholder fetch, returns dummy structure until API integrated."""
        return {
            "title": "Sample Doc",
            "content": "Your test content...",
            "mime_type": "text/plain",
            "owner": "you@example.com",
            "content_hash": "abc123",
        }
        raise NotImplementedError("Google Docs API integration pending")
