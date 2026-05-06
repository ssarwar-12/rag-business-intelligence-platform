import pytest

from app.ingestion.chunking import TextSection, approx_token_count, chunk_sections


def test_chunk_sections_adds_overlap_and_metadata() -> None:
    text = "abcdefghijklmnopqrstuvwxyz"

    chunks = chunk_sections(
        [TextSection(text=text, metadata={"page": 1})],
        chunk_size=10,
        overlap=2,
    )

    assert [chunk.text for chunk in chunks] == ["abcdefghij", "ijklmnopqr", "qrstuvwxyz"]
    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]
    assert chunks[0].metadata["page"] == 1
    assert chunks[1].metadata["char_start"] == 8


def test_chunk_sections_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        chunk_sections([TextSection(text="hello")], chunk_size=100, overlap=100)


def test_approx_token_count_never_returns_zero() -> None:
    assert approx_token_count("") == 1
    assert approx_token_count("one two three") == 3
