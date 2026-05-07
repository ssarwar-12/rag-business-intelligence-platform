from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.ingestion.chunking import TextChunk, chunk_sections
from app.ingestion.loaders import extract_document
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.rag.embeddings import EmbeddingClient, OpenAIEmbeddingClient
from app.vectorstores.base import EmbeddedChunk, VectorStore
from app.vectorstores.factory import get_vector_store


def ingest_document(
    db: Session,
    document: Document,
    *,
    embedding_client: EmbeddingClient | None = None,
    vector_store: VectorStore | None = None,
) -> Document:
    actual_embedding_client = embedding_client or OpenAIEmbeddingClient()
    actual_vector_store = vector_store or get_vector_store()

    document.status = DocumentStatus.processing
    document.error_message = None
    db.add(document)
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
    db.commit()
    db.refresh(document)

    try:
        chunks = _build_chunks(document)
        chunk_rows = _store_chunks(db, document, chunks)
        _upsert_vectors(
            chunk_rows,
            embedding_client=actual_embedding_client,
            vector_store=actual_vector_store,
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
        actual_vector_store.delete_document(str(document.id))
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


def _store_chunks(db: Session, document: Document, chunks: list[TextChunk]) -> list[DocumentChunk]:
    rows: list[DocumentChunk] = []
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
        rows.append(chunk_row)

    db.flush()
    return rows


def _upsert_vectors(
    chunk_rows: list[DocumentChunk],
    *,
    embedding_client: EmbeddingClient,
    vector_store: VectorStore,
) -> None:
    embeddings = embedding_client.embed_texts([chunk.text for chunk in chunk_rows])
    if len(embeddings) != len(chunk_rows):
        raise ValueError("Embedding count did not match generated chunk count")

    vector_store.upsert(
        [
            EmbeddedChunk(
                id=str(chunk.vector_id),
                document_id=str(chunk.document_id),
                workspace_id=str(chunk.workspace_id),
                embedding=embedding,
                metadata=chunk.metadata_ or {},
            )
            for chunk, embedding in zip(chunk_rows, embeddings, strict=True)
        ]
    )
