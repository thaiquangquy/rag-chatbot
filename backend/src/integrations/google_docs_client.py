"""Google Docs API client abstraction."""

from __future__ import annotations

from typing import Any


class GoogleDocsClient:
    def __init__(self, credentials_path: str | None = None) -> None:
        self.credentials_path = credentials_path

    def fetch_document(self, document_id: str) -> dict[str, Any]:
        """Placeholder fetch, returns dummy structure until API integrated."""
        raise NotImplementedError("Google Docs API integration pending")
