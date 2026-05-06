from app.ingestion.csv_summary import csv_rows_to_text, summarize_csv


def test_summarize_csv_returns_numeric_and_missing_value_stats(tmp_path) -> None:
    csv_path = tmp_path / "sales.csv"
    csv_path.write_text(
        "category,revenue,region\nSoftware,100,West\nServices,200,\nHardware,300,East\n",
        encoding="utf-8",
    )

    summary = summarize_csv(csv_path)

    assert summary["columns"] == ["category", "revenue", "region"]
    assert summary["row_count"] == 3
    assert summary["numeric_columns"]["revenue"] == {
        "min": 100.0,
        "max": 300.0,
        "mean": 200.0,
    }
    assert summary["missing_values"]["region"] == 1


def test_csv_rows_to_text_converts_rows_to_searchable_text(tmp_path) -> None:
    csv_path = tmp_path / "sales.csv"
    csv_path.write_text("category,revenue\nSoftware,100\n", encoding="utf-8")

    text = csv_rows_to_text(csv_path)

    assert "Row 1:" in text
    assert "category: Software" in text
    assert "revenue: 100" in text
