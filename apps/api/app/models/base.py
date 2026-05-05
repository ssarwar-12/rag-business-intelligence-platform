from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON, TypeDecorator, Uuid


class JSONBType(TypeDecorator):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())


class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSONBType(),
        list[str]: JSONBType(),
        UUID: Uuid(as_uuid=True),
    }


def uuid_pk() -> Mapped[UUID]:
    return mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def created_at_column() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
