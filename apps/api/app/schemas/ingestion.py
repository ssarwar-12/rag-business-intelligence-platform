from pydantic import BaseModel

from app.schemas.document import DocumentRead


class IngestionResponse(BaseModel):
    document: DocumentRead
    chunk_count: int
