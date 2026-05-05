from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_demo_user
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user),
) -> Workspace:
    workspace = Workspace(name=payload.name, owner_id=user.id)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


@router.get("", response_model=list[WorkspaceRead])
def list_workspaces(
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user),
) -> list[Workspace]:
    return list(
        db.scalars(
            select(Workspace)
            .where(Workspace.owner_id == user.id)
            .order_by(Workspace.created_at.desc())
        )
    )
