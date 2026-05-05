from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class DocumentRead(BaseModel):
    id: UUID
    workspace_id: UUID
    filename: str
    file_type: str
    status: DocumentStatus
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
