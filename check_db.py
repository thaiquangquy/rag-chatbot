from backend.src.cli.ingest_cli import session_scope
from backend.src.models.entities import Section, Document

with session_scope() as session:
    sections = session.query(Section).all()
    documents = session.query(Document).all()
    print(f"Found {len(documents)} documents")
    print(f"Found {len(sections)} sections")
    if sections:
        print(f"\nFirst section content:")
        print(sections[0].content[:200])
