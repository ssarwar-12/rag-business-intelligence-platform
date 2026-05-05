from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class WorkspaceRead(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
