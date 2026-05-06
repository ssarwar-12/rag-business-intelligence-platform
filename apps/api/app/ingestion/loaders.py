from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from app.ingestion.chunking import TextSection
from app.ingestion.csv_summary import csv_rows_to_text, summarize_csv


@dataclass(frozen=True)
class ExtractedDocument:
    sections: list[TextSection]


def extract_document(path: Path, file_type: str) -> ExtractedDocument:
    match file_type:
        case "pdf":
            return _extract_pdf(path)
        case "txt" | "md":
            return _extract_text(path, file_type)
        case "csv":
            return _extract_csv(path)
        case _:
            raise ValueError(f"Unsupported file type: {file_type}")


def _extract_pdf(path: Path) -> ExtractedDocument:
    reader = PdfReader(str(path))
    sections: list[TextSection] = []

    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            sections.append(TextSection(text=text, metadata={"page": page_index, "source_type": "pdf"}))

    if not sections:
        raise ValueError("No extractable text found in PDF")

    return ExtractedDocument(sections=sections)


def _extract_text(path: Path, file_type: str) -> ExtractedDocument:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("No text found in document")
    return ExtractedDocument(sections=[TextSection(text=text, metadata={"source_type": file_type})])


def _extract_csv(path: Path) -> ExtractedDocument:
    summary = summarize_csv(path)
    text = csv_rows_to_text(path)
    if not text.strip():
        raise ValueError("No rows found in CSV")
    return ExtractedDocument(
        sections=[
            TextSection(
                text=text,
                metadata={
                    "source_type": "csv",
                    "csv_summary": summary,
                },
            )
        ]
    )
