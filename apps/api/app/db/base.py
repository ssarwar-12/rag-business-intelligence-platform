from app.models.base import Base

# Import models so Alembic and create_all can discover table metadata.
from app.models.conversation import Conversation  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.document_chunk import DocumentChunk  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.query_log import QueryLog  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.workspace import Workspace  # noqa: F401

__all__ = ["Base"]
