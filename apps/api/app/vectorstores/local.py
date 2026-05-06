from __future__ import annotations

import json
import math
from pathlib import Path

from app.vectorstores.base import EmbeddedChunk, SearchResult


class LocalVectorStore:
    def __init__(self, path: Path | str = "./local_vector_store.json") -> None:
        self.path = Path(path)

    def upsert(self, chunks: list[EmbeddedChunk]) -> None:
        records = self._load()
        for chunk in chunks:
            records[chunk.id] = {
                "id": chunk.id,
                "document_id": chunk.document_id,
                "workspace_id": chunk.workspace_id,
                "embedding": chunk.embedding,
                "metadata": chunk.metadata,
            }
        self._save(records)

    def query(
        self,
        workspace_id: str,
        query_embedding: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        records = self._load()
        scored: list[SearchResult] = []

        for record in records.values():
            if record["workspace_id"] != workspace_id:
                continue
            score = _cosine_similarity(query_embedding, record["embedding"])
            scored.append(
                SearchResult(
                    chunk_id=record["id"],
                    document_id=record["document_id"],
                    workspace_id=record["workspace_id"],
                    score=score,
                )
            )

        return sorted(scored, key=lambda result: result.score, reverse=True)[:top_k]

    def delete_document(self, document_id: str) -> None:
        records = self._load()
        filtered = {
            key: record for key, record in records.items() if record["document_id"] != document_id
        }
        self._save(filtered)

    def _load(self) -> dict[str, dict]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, records: dict[str, dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0

    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
