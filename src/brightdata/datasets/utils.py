"""
Dataset utilities - helpers for exporting and processing dataset results.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Leading characters spreadsheet apps treat as the start of a formula.
_FORMULA_TRIGGER_CHARS = ("=", "+", "-", "@", "\t", "\r")


def export_json(
    data: List[Dict[str, Any]],
    filepath: Union[str, Path],
    indent: int = 2,
) -> Path:
    """
    Export dataset results to JSON file.

    Args:
        data: List of records from download()
        filepath: Output file path
        indent: JSON indentation (default: 2)

    Returns:
        Path to the created file
    """
    filepath = Path(filepath)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str, ensure_ascii=False)
    return filepath


def export_jsonl(
    data: List[Dict[str, Any]],
    filepath: Union[str, Path],
) -> Path:
    """
    Export dataset results to JSONL (newline-delimited JSON) file.

    Args:
        data: List of records from download()
        filepath: Output file path

    Returns:
        Path to the created file
    """
    filepath = Path(filepath)
    with open(filepath, "w", encoding="utf-8") as f:
        for record in data:
            f.write(json.dumps(record, default=str, ensure_ascii=False) + "\n")
    return filepath


def _sanitize_csv_cell(value: Any) -> Any:
    """
    Neutralize spreadsheet formula injection (CWE-1236) in a single CSV cell.

    Strings starting with '=', '+', '-', '@', a tab, or a carriage return are
    prefixed with a leading single quote, which spreadsheet applications
    treat as an explicit "text" marker instead of executing the value as a
    formula (e.g. HYPERLINK/WEBSERVICE/IMPORTXML/DDE payloads).
    """
    if isinstance(value, str) and value.startswith(_FORMULA_TRIGGER_CHARS):
        return "'" + value
    return value


def export_csv(
    data: List[Dict[str, Any]],
    filepath: Union[str, Path],
    fields: Optional[List[str]] = None,
    flatten_nested: bool = True,
    sanitize: bool = True,
) -> Path:
    """
    Export dataset results to CSV file.

    Args:
        data: List of records from download()
        filepath: Output file path
        fields: Specific fields to export (default: all fields from first record)
        flatten_nested: Convert nested objects/arrays to JSON strings (default: True)
        sanitize: Escape cell values that would be interpreted as formulas by
            spreadsheet applications (leading '=', '+', '-', '@', tab, or CR),
            preventing CSV/formula injection (CWE-1236). Default: True.

    Returns:
        Path to the created file
    """
    if not data:
        filepath = Path(filepath)
        filepath.touch()
        return filepath

    filepath = Path(filepath)

    # Determine fields
    if fields is None:
        fields = list(data[0].keys())

    # Process data
    processed_data = []
    for record in data:
        row = {}
        for field in fields:
            value = record.get(field)
            if flatten_nested and isinstance(value, (dict, list)):
                value = json.dumps(value, default=str, ensure_ascii=False)
            if sanitize:
                value = _sanitize_csv_cell(value)
            row[field] = value
        processed_data.append(row)

    # Write CSV
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(processed_data)

    return filepath


def export(
    data: List[Dict[str, Any]],
    filepath: Union[str, Path],
    **kwargs,
) -> Path:
    """
    Export dataset results to file. Format is auto-detected from extension.

    Supported formats:
        - .json: JSON format
        - .jsonl, .ndjson: JSONL (newline-delimited JSON)
        - .csv: CSV format

    Args:
        data: List of records from download()
        filepath: Output file path (extension determines format)
        **kwargs: Additional arguments passed to format-specific exporter

    Returns:
        Path to the created file

    Raises:
        ValueError: If file extension is not supported
    """
    filepath = Path(filepath)
    ext = filepath.suffix.lower()

    if ext == ".json":
        return export_json(data, filepath, **kwargs)
    elif ext in (".jsonl", ".ndjson"):
        return export_jsonl(data, filepath)
    elif ext == ".csv":
        return export_csv(data, filepath, **kwargs)
    else:
        raise ValueError(
            f"Unsupported file extension: {ext}. " f"Supported: .json, .jsonl, .ndjson, .csv"
        )
