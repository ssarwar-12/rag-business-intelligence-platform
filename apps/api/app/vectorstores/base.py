from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class EmbeddedChunk:
    id: str
    document_id: str
    workspace_id: str
    embedding: list[float]
    metadata: dict[str, str | int | float | bool | None] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    document_id: str
    workspace_id: str
    score: float


class VectorStore(Protocol):
    def upsert(self, chunks: list[EmbeddedChunk]) -> None:
        ...

    def query(
        self,
        workspace_id: str,
        query_embedding: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        ...

    def delete_document(self, document_id: str) -> None:
        ...
