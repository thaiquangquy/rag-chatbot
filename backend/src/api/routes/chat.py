"""Chat endpoint."""

from __future__ import annotations

from backend.src.middleware.auth import api_key_guard
from backend.src.models.schemas import ChatRequest, ChatResponse, SectionSource
from backend.src.services.answer_service import AnswerService
from backend.src.services.retrieval_service import RetrievalService
from backend.src.utils.source_link import build_source_link
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(dependencies=[Depends(api_key_guard)])


def get_db() -> Session:
    raise NotImplementedError("Database session dependency not yet wired")


def get_retrieval_service() -> RetrievalService:
    raise NotImplementedError


def get_answer_service() -> AnswerService:
    return AnswerService()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    retrieval: RetrievalService = Depends(get_retrieval_service),
    answer_service: AnswerService = Depends(get_answer_service),
) -> ChatResponse:
    sections = retrieval.retrieve(request.query, top_k=request.top_k)
    section_texts = [section.content for section in sections]
    response_id, generated_text = answer_service.answer(request.query, section_texts)
    sources = [
        SectionSource(
            document_id=section.document_id,
            section_id=section.section_id,
            snippet=section.content[:200],
            url=build_source_link(section),
        )
        for section in sections
    ]
    return ChatResponse(response_id=response_id, generated_text=generated_text, sources=sources)
