from app.ingestion.loaders import extract_document


def test_extract_txt_document(tmp_path) -> None:
    text_path = tmp_path / "notes.txt"
    text_path.write_text("Quarterly revenue increased in software.", encoding="utf-8")

    extracted = extract_document(text_path, "txt")

    assert len(extracted.sections) == 1
    assert "software" in extracted.sections[0].text
    assert extracted.sections[0].metadata["source_type"] == "txt"
