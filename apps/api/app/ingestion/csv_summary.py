from pathlib import Path
from typing import Any

import pandas as pd


def summarize_csv(path: Path) -> dict[str, Any]:
    dataframe = pd.read_csv(path)
    numeric_summary: dict[str, dict[str, float | None]] = {}

    for column in dataframe.select_dtypes(include="number").columns:
        series = dataframe[column]
        numeric_summary[str(column)] = {
            "min": _finite_or_none(series.min()),
            "max": _finite_or_none(series.max()),
            "mean": _finite_or_none(series.mean()),
        }

    missing_values = {
        str(column): int(count) for column, count in dataframe.isna().sum().to_dict().items()
    }

    return {
        "columns": [str(column) for column in dataframe.columns],
        "row_count": int(len(dataframe)),
        "numeric_columns": numeric_summary,
        "missing_values": missing_values,
    }


def csv_rows_to_text(path: Path) -> str:
    dataframe = pd.read_csv(path)
    lines: list[str] = []

    for index, row in dataframe.iterrows():
        values = [f"{column}: {row[column]}" for column in dataframe.columns]
        lines.append(f"Row {index + 1}: " + "; ".join(values))

    return "\n".join(lines)


def _finite_or_none(value: Any) -> float | None:
    if pd.isna(value):
        return None
    return float(value)
