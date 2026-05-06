from sqlalchemy import func, select

from app.core.demo_user import ensure_demo_user
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.ingestion.pipeline import ingest_document
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.models.workspace import Workspace


def test_ingest_document_success_stores_chunks(tmp_path) -> None:
    Base.metadata.create_all(bind=engine)
    source = tmp_path / "memo.txt"
    source.write_text("Revenue grew in software and services. " * 300, encoding="utf-8")

    with SessionLocal() as db:
        user = ensure_demo_user(db)
        workspace = Workspace(name="Ingestion success", owner_id=user.id)
        db.add(workspace)
        db.flush()
        document = Document(
            workspace_id=workspace.id,
            filename="memo.txt",
            file_type="txt",
            storage_path=str(source),
            status=DocumentStatus.uploaded,
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        result = ingest_document(db, document)
        chunk_count = db.scalar(
            select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == result.id)
        )

    assert result.status == DocumentStatus.completed
    assert result.error_message is None
    assert chunk_count and chunk_count > 0


def test_ingest_document_failure_marks_document_failed(tmp_path) -> None:
    Base.metadata.create_all(bind=engine)
    missing_source = tmp_path / "missing.txt"

    with SessionLocal() as db:
        user = ensure_demo_user(db)
        workspace = Workspace(name="Ingestion failure", owner_id=user.id)
        db.add(workspace)
        db.flush()
        document = Document(
            workspace_id=workspace.id,
            filename="missing.txt",
            file_type="txt",
            storage_path=str(missing_source),
            status=DocumentStatus.uploaded,
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        result = ingest_document(db, document)

    assert result.status == DocumentStatus.failed
    assert result.error_message
