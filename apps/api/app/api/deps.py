from collections.abc import Generator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.demo_user import ensure_demo_user
from app.db.session import SessionLocal
from app.models.user import User
from app.models.workspace import Workspace


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_demo_user(db: Session = Depends(get_db)) -> User:
    return ensure_demo_user(db)


def get_demo_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user),
) -> Workspace:
    workspace = db.scalar(
        select(Workspace).where(Workspace.id == workspace_id, Workspace.owner_id == user.id)
    )
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    return workspace
