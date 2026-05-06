from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.ingestion.chunking import TextChunk, chunk_sections
from app.ingestion.loaders import extract_document
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk


def ingest_document(db: Session, document: Document) -> Document:
    document.status = DocumentStatus.processing
    document.error_message = None
    db.add(document)
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
    db.commit()
    db.refresh(document)

    try:
        chunks = _build_chunks(document)
        _store_chunks(db, document, chunks)
    except Exception as exc:
        document.status = DocumentStatus.failed
        document.error_message = str(exc)[:2048]
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    document.status = DocumentStatus.completed
    document.error_message = None
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def _build_chunks(document: Document) -> list[TextChunk]:
    path = Path(document.storage_path)
    if not path.exists():
        raise FileNotFoundError(f"Uploaded file not found: {path}")

    extracted = extract_document(path, document.file_type)
    chunks = chunk_sections(extracted.sections)
    if not chunks:
        raise ValueError("No chunks generated from document")
    return chunks


def _store_chunks(db: Session, document: Document, chunks: list[TextChunk]) -> None:
    for chunk in chunks:
        chunk_row = DocumentChunk(
            document_id=document.id,
            workspace_id=document.workspace_id,
            chunk_index=chunk.chunk_index,
            text=chunk.text,
            token_count=chunk.token_count,
            metadata_=chunk.metadata,
            vector_id=f"{document.id}:{chunk.chunk_index}",
        )
        db.add(chunk_row)

    db.commit()
