from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JSONBType, created_at_column, uuid_pk


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[UUID] = uuid_pk()
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    conversation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retrieved_chunk_ids: Mapped[list[str]] = mapped_column(JSONBType(), default=list)
    created_at = created_at_column()

    workspace: Mapped["Workspace"] = relationship(back_populates="query_logs")
    conversation: Mapped["Conversation | None"] = relationship(back_populates="query_logs")
