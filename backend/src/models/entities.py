"""SQLAlchemy ORM models for RAG chatbot."""

from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    owner: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    last_indexed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    content_hash: Mapped[str] = mapped_column(String, nullable=False)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ingestion_status: Mapped[str] = mapped_column(Enum("pending", "succeeded", "failed", name="ingestion_status"), nullable=False)
    extra_metadata: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    sections: Mapped[List["Section"]] = relationship("Section", back_populates="document", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"

    section_id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(String, ForeignKey("documents.document_id"), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    char_offset_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    char_offset_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    embedding_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="sections")


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_active_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Query(Base):
    __tablename__ = "queries"

    query_id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    embedding_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    conversation_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("conversations.conversation_id"))

    conversation: Mapped[Optional["Conversation"]] = relationship("Conversation")


class Response(Base):
    __tablename__ = "responses"

    response_id: Mapped[str] = mapped_column(String, primary_key=True)
    query_id: Mapped[str] = mapped_column(String, ForeignKey("queries.query_id"), nullable=False)
    generated_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_sections: Mapped[Any] = mapped_column(JSON, nullable=False, default=list)
    confidence_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    query: Mapped["Query"] = relationship("Query")
