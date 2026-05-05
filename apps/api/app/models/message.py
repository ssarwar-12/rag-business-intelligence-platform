from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, JSONBType, created_at_column, uuid_pk


class MessageRole(StrEnum):
    user = "user"
    assistant = "assistant"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = uuid_pk()
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole, name="message_role"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSONBType(), default=dict)
    created_at = created_at_column()

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
