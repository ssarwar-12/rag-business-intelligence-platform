from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_demo_workspace
from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.models.workspace import Workspace
from app.schemas.document import DocumentRead

router = APIRouter(prefix="/workspaces/{workspace_id}/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {"pdf", "txt", "md", "csv"}


def _safe_filename(filename: str) -> str:
    name = Path(filename).name.strip()
    return name or f"upload-{uuid4()}"


def _file_extension(filename: str) -> str:
    extension = Path(filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Upload PDF, TXT, MD, or CSV files.",
        )
    return extension


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    workspace_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_demo_workspace),
) -> Document:
    filename = _safe_filename(file.filename or "")
    file_type = _file_extension(filename)

    document = Document(
        workspace_id=workspace.id,
        filename=filename,
        file_type=file_type,
        storage_path="",
        status=DocumentStatus.uploaded,
    )
    db.add(document)
    db.flush()

    destination_dir = settings.upload_dir / str(workspace_id) / str(document.id)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination_path = destination_dir / filename

    with destination_path.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            output.write(chunk)

    document.storage_path = str(destination_path)
    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentRead])
def list_documents(
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(get_demo_workspace),
) -> list[Document]:
    return list(
        db.scalars(
            select(Document)
            .where(Document.workspace_id == workspace.id)
            .order_by(Document.created_at.desc())
        )
    )
