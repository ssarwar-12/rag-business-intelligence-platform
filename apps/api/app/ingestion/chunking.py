from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TextSection:
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TextChunk:
    text: str
    chunk_index: int
    token_count: int
    metadata: dict[str, Any]


def chunk_sections(
    sections: list[TextSection],
    *,
    chunk_size: int = 3500,
    overlap: int = 450,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[TextChunk] = []
    for section in sections:
        text = _normalize_text(section.text)
        if not text:
            continue

        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    TextChunk(
                        text=chunk_text,
                        chunk_index=len(chunks),
                        token_count=approx_token_count(chunk_text),
                        metadata={
                            **section.metadata,
                            "char_start": start,
                            "char_end": end,
                        },
                    )
                )
            if end == len(text):
                break
            start = end - overlap

    return chunks


def approx_token_count(text: str) -> int:
    return max(1, len(text.split()))


def _normalize_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()
