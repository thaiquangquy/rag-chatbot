"""Chat endpoint."""

from __future__ import annotations

from typing import cast
from typing import Iterator

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.cli.ingest_cli import session_scope
from backend.src.config.settings import get_settings
from backend.src.middleware.auth import api_key_guard
from backend.src.models.schemas import ChatRequest, ChatResponse, SectionSource
from backend.src.services.answer_service import AnswerResult, AnswerService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.services.suggest_service import SuggestService
from backend.src.utils.source_link import build_source_link
from backend.src.vector.faiss_index import VectorIndex

router = APIRouter(dependencies=[Depends(api_key_guard)])

_settings = get_settings()
_vector_index = VectorIndex(_settings.embedding_dimension)


def get_db() -> Iterator[Session]:
    """Yield a database session for FastAPI dependency injection."""
    with session_scope() as session:
        yield session


def get_retrieval_service(db: Session = Depends(get_db)) -> RetrievalService:
    return RetrievalService(db=db, vector_index=_vector_index)


def get_answer_service() -> AnswerService:
    return AnswerService()


def get_suggest_service() -> SuggestService:
    return SuggestService()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    retrieval: RetrievalService = Depends(get_retrieval_service),
    answer_service: AnswerService = Depends(get_answer_service),
    suggest_service: SuggestService = Depends(get_suggest_service),
) -> ChatResponse:
    sections = retrieval.retrieve(request.query, top_k=request.top_k)
    section_texts = [cast(str, section.content) for section in sections]
    result: AnswerResult = answer_service.answer(request.query, section_texts)
    sources = [
        SectionSource(
            document_id=cast(str, section.document_id),
            section_id=cast(str, section.section_id),
            snippet=cast(str, section.content)[:200],
            url=build_source_link(section),
        )
        for section in sections
    ]
    related_topics = (
        suggest_service.suggest_related_topics(request.query)
        if result.is_fallback
        else []
    )
    return ChatResponse(
        response_id=result.response_id,
        generated_text=result.generated_text,
        sources=sources,
        is_fallback=result.is_fallback,
        related_topics=related_topics,
    )
