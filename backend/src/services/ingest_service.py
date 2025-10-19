"""Ingestion pipeline service."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.src.integrations.google_docs_client import GoogleDocsClient
from backend.src.lib.chunking import chunk_text
from backend.src.lib.embedding import embed_texts
from backend.src.models import entities
from backend.src.vector.faiss_index import VectorIndex


class IngestService:
    def __init__(
        self,
        db: Session,
        docs_client: GoogleDocsClient,
        vector_index: VectorIndex,
    ) -> None:
        self.db = db
        self.docs_client = docs_client
        self.vector_index = vector_index

    def ingest(self, document_id: str, *, source_url: str) -> str:
        document_data = self.docs_client.fetch_document(document_id)
        content = document_data["content"]
        title = document_data.get("title", "Untitled")
        chunks = chunk_text(content)
        embeddings = embed_texts(chunks)
        section_ids = [str(uuid.uuid4()) for _ in chunks]

        document = entities.Document(
            document_id=document_id,
            title=title,
            url=source_url,
            mime_type=document_data.get("mime_type", "text/plain"),
            owner=document_data.get("owner"),
            content_hash=document_data.get("content_hash", ""),
            ingestion_status="succeeded",
        )
        self.db.merge(document)
        for sid, chunk, embedding in zip(section_ids, chunks, embeddings):
            section = entities.Section(
                section_id=sid,
                document_id=document_id,
                content=chunk,
            )
            self.db.merge(section)
        self.db.commit()

        self.vector_index.add(section_ids, embeddings)
        return str(uuid.uuid4())
