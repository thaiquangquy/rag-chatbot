"""Ingestion endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.middleware.auth import api_key_guard
from backend.src.models.schemas import IngestRequest, IngestResponse
from backend.src.services.ingest_service import IngestService

router = APIRouter(dependencies=[Depends(api_key_guard)])


def get_db() -> Session:
    raise NotImplementedError


def get_ingest_service() -> IngestService:
    raise NotImplementedError


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
