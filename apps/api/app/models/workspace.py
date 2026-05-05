from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, created_at_column, uuid_pk


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = created_at_column()

    owner: Mapped["User"] = relationship(back_populates="workspaces")
    documents: Mapped[list["Document"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    query_logs: Mapped[list["QueryLog"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
