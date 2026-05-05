from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, created_at_column, uuid_pk


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    created_at = created_at_column()

    workspaces: Mapped[list["Workspace"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )
