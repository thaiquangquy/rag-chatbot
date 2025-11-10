"""Refresh ingestion pipeline for existing documents."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy.orm import Session

from backend.src.integrations.google_docs_client import GoogleDocsClient
from backend.src.lib.chunking import chunk_text
from backend.src.lib.embedding import embed_texts
from backend.src.models import entities
from backend.src.vector.faiss_index import VectorIndex


class RefreshService:
    """Re-index documents when source content changes."""

    def __init__(
        self,
        db: Session,
        docs_client: GoogleDocsClient,
        vector_index: VectorIndex,
        index_path: str | None = None,
    ) -> None:
        self.db = db
        self.docs_client = docs_client
        self.vector_index = vector_index
        self.index_path = index_path

    def refresh(self, document_id: str, *, source_url: str, force: bool = False) -> str:
        document_data = self.docs_client.fetch_document(document_id)
        content = document_data.get("content", "")
        new_hash = document_data.get("content_hash", "")

        document = self.db.get(entities.Document, document_id)
        if document and document.content_hash == new_hash and not force:
            return str(uuid.uuid4())

        if document is None:
            document = entities.Document(
                document_id=document_id,
                title=document_data.get("title", "Untitled"),
                url=source_url,
                mime_type=document_data.get("mime_type", "text/plain"),
                owner=document_data.get("owner"),
                content_hash=new_hash,
                size_bytes=document_data.get("size_bytes"),
                ingestion_status="pending",
                extra_metadata=document_data.get("extra_metadata"),
            )
            self.db.add(document)
            self.db.flush()
        else:
            existing_sections: Sequence[entities.Section] = list(document.sections)
            section_ids = [str(section.section_id) for section in existing_sections]
            if section_ids:
                self.vector_index.remove(section_ids)
            for section in existing_sections:
                self.db.delete(section)
            document.title = document_data.get("title", document.title)
            document.url = source_url
            document.mime_type = document_data.get("mime_type", document.mime_type)
            document.owner = document_data.get("owner", document.owner)
            document.content_hash = new_hash or document.content_hash
            document.size_bytes = document_data.get("size_bytes", document.size_bytes)
            document.extra_metadata = document_data.get("extra_metadata", document.extra_metadata)
            document.ingestion_status = "pending"

        chunks = chunk_text(content)
        embeddings = embed_texts(chunks) if chunks else None
        section_ids = [str(uuid.uuid4()) for _ in chunks]
        for sid, chunk in zip(section_ids, chunks):
            section = entities.Section(
                section_id=sid,
                document_id=document_id,
                content=chunk,
            )
            self.db.add(section)

        if chunks and embeddings is not None:
            self.vector_index.add(section_ids, embeddings)

        document.ingestion_status = "succeeded"
        document.last_indexed = entities.utcnow()
        if content:
            document.size_bytes = len(content.encode("utf-8"))

        self.db.commit()
        
        # Persist the index to disk if path is configured
        if self.index_path:
            self.vector_index.save(self.index_path)
        
        return str(uuid.uuid4())
