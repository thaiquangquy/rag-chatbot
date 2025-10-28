"""Build source links for Google Docs sections."""

from __future__ import annotations

from backend.src.models.entities import Section


def build_source_link(section: Section) -> str:
    """
    Build a Google Docs link to a specific section.
    
    For Google Docs, we can link to:
    - The document itself: https://docs.google.com/document/d/{document_id}/edit
    - A specific heading: https://docs.google.com/document/d/{document_id}/edit#heading=h.{heading_id}
    
    Since we may not have heading IDs, we'll use character offset as a bookmark if available,
    or just link to the document root.
    
    Args:
        section: The Section entity containing document_id and metadata
        
    Returns:
        A clickable Google Docs URL
    """
    if not section.document:
        return ""
    
    base_url = section.document.url
    
    # If the document URL is already a full Google Docs URL, use it
    if base_url.startswith("http"):
        return base_url
    
    # Otherwise, construct from document_id
    document_id = section.document_id
    url = f"https://docs.google.com/document/d/{document_id}/edit"
    
    # If we have a section title that could be a heading, try to link to it
    # Google Docs uses heading anchors like #heading=h.{id}
    # For now, we'll just link to the document; in a production system,
    # we'd need to extract heading IDs during ingestion
    
    return url
