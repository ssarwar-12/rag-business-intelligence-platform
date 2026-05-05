from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, created_at_column, uuid_pk


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[UUID] = uuid_pk()
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New conversation")
    created_at = created_at_column()

    workspace: Mapped["Workspace"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    query_logs: Mapped[list["QueryLog"]] = relationship(back_populates="conversation")
