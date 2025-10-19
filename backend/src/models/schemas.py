"""Pydantic API schemas."""

from datetime import datetime
from typing import Literal, Sequence

from pydantic import BaseModel, Field


class SectionSource(BaseModel):
    document_id: str
    section_id: str
    snippet: str
    url: str


class ChatRequest(BaseModel):
    query: str
    session_id: str
    top_k: int = Field(default=5, ge=1, le=10)


class ChatResponse(BaseModel):
    response_id: str
    generated_text: str
    sources: Sequence[SectionSource]


class IngestRequest(BaseModel):
    document_id: str
    source: str


class IngestResponse(BaseModel):
    task_id: str


class DocumentSchema(BaseModel):
    document_id: str
    title: str
    url: str
    mime_type: str
    owner: str | None
    created_at: datetime
    updated_at: datetime
    last_indexed: datetime | None
    ingestion_status: Literal["pending", "succeeded", "failed"]
