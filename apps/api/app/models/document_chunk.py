from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JSONBType, created_at_column, uuid_pk


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[UUID] = uuid_pk()
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONBType(), default=dict)
    vector_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at = created_at_column()

    document: Mapped["Document"] = relationship(back_populates="chunks")
