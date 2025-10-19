"""SQLAlchemy ORM models for RAG chatbot."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_indexed = Column(DateTime, nullable=True)
    content_hash = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=True)
    ingestion_status = Column(Enum("pending", "succeeded", "failed", name="ingestion_status"), nullable=False)
    extra_metadata = Column(JSON, nullable=True)

    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"

    section_id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.document_id"), nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    char_offset_start = Column(Integer, nullable=True)
    char_offset_end = Column(Integer, nullable=True)
    embedding_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="sections")


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Query(Base):
    __tablename__ = "queries"

    query_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    session_id = Column(String, nullable=False)
    embedding_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    conversation_id = Column(String, ForeignKey("conversations.conversation_id"))

    conversation = relationship("Conversation")


class Response(Base):
    __tablename__ = "responses"

    response_id = Column(String, primary_key=True)
    query_id = Column(String, ForeignKey("queries.query_id"), nullable=False)
    generated_text = Column(Text, nullable=False)
    source_sections = Column(JSON, nullable=False, default=list)
    confidence_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    query = relationship("Query")
