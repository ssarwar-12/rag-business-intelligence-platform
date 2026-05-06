from app.core.config import settings
from app.vectorstores.local import LocalVectorStore


def get_vector_store() -> LocalVectorStore:
    if settings.vector_store != "local":
        raise ValueError(f"Unsupported vector store for Phase 2: {settings.vector_store}")
    return LocalVectorStore()
