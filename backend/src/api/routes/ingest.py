"""Ingestion endpoint."""

from __future__ import annotations
from typing import Iterator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.cli.ingest_cli import session_scope  # existing helper used by ingest_cli
from backend.src.config.settings import get_settings
from backend.src.integrations.google_docs_client import GoogleDocsClient
from backend.src.middleware.auth import api_key_guard
from backend.src.models.schemas import IngestRequest, IngestResponse
from backend.src.services.ingest_service import IngestService
from backend.src.vector.faiss_index import VectorIndex

router = APIRouter(dependencies=[Depends(api_key_guard)])

_settings = get_settings()

def get_db() -> Iterator[Session]:
    """FastAPI-compatible dependency that yields a DB session."""
    with session_scope() as session:
        yield session

    # raise NotImplementedError

def get_ingest_service(db: Session = Depends(get_db)) -> IngestService:
    docs_client = GoogleDocsClient(_settings.service_account_path)
    vector_index = VectorIndex(_settings.embedding_dimension)
    return IngestService(db=db, docs_client=docs_client, vector_index=vector_index)


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest(
    request: IngestRequest,
    ingest_service: IngestService = Depends(get_ingest_service),
) -> IngestResponse:
    try:
        task_id = ingest_service.ingest(request.document_id, source_url=request.source)
    except Exception as exc:  # pragma: no cover - placeholder until real errors defined
        raise HTTPException(status_code=500, detail="Failed to ingest document") from exc
    return IngestResponse(task_id=task_id)
