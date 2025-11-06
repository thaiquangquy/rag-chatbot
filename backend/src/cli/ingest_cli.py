"""Administrative CLI for triggering document ingestion."""

from __future__ import annotations

import argparse
import sys
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.src.config.settings import get_settings
from backend.src.integrations.google_docs_client import GoogleDocsClient
from backend.src.services.ingest_service import IngestService
from backend.src.services.refresh_service import RefreshService
from backend.src.vector.faiss_index import VectorIndex


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trigger ingestion jobs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest a new document")
    ingest_parser.add_argument("document_id", help="Source document identifier")
    ingest_parser.add_argument("--source", required=True, help="Canonical document URL")

    refresh_parser = subparsers.add_parser("refresh", help="Refresh an existing document")
    refresh_parser.add_argument("document_id", help="Source document identifier")
    refresh_parser.add_argument("--source", required=True, help="Canonical document URL")
    refresh_parser.add_argument("--force", action="store_true", help="Force reindex even if content hash unchanged")

    return parser.parse_args(argv)


def build_dependencies() -> tuple[GoogleDocsClient, VectorIndex]:
    settings = get_settings()
    docs_client = GoogleDocsClient(settings.service_account_path)
    vector_index = VectorIndex(settings.embedding_dimension)
    return docs_client, vector_index


@contextmanager
def session_scope() -> Iterator[Session]:
    settings = get_settings()
    engine = create_engine(settings.database_url, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    with session_scope() as session:
        docs_client, vector_index = build_dependencies()
        try:
            if args.command == "refresh":
                service = RefreshService(session, docs_client, vector_index)
                task_id = service.refresh(args.document_id, source_url=args.source, force=args.force)
            else:
                service = IngestService(session, docs_client, vector_index)
                task_id = service.ingest(args.document_id, source_url=args.source)
        except NotImplementedError as exc:
            print("Google Docs client is not implemented yet:", exc, file=sys.stderr)
            return 2
        except Exception as exc:
            print(f"Failed to schedule ingestion: {exc}", file=sys.stderr)
            return 1
    print(f"Enqueued ingestion task {task_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
