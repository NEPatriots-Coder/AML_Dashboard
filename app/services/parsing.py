import csv
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Any

HEADER_SENTINELS = {"SITE LOGGING MOVEMENT", "DATE", "MOVEMENT TYPE", "BIN"}


def _normalize_header(value: str) -> str:
    value = value.strip().lower()
    value = value.replace("/", " ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def _record_with_source_key(record: dict[str, str]) -> dict[str, str]:
    hash_input = "||".join(record.get(k, "") for k in sorted(record.keys()))
    record["_source_key"] = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
    return record


def _build_headers(raw_headers: list[str]) -> list[str]:
    headers = []
    for i, header in enumerate(raw_headers):
        normalized = _normalize_header(header) if header.strip() else f"unnamed_{i}"
        headers.append(normalized)
    return headers


def normalize_matrix_rows(raw_rows: list[list[Any]]) -> list[dict[str, str]]:
    if not raw_rows:
        return []

    rows = [[str(cell) if cell is not None else "" for cell in row] for row in raw_rows]
    header_idx = find_header_index(rows)
    headers = _build_headers(rows[header_idx])

    records: list[dict[str, str]] = []
    for row in rows[header_idx + 1 :]:
        if not any(cell.strip() for cell in row):
            continue

        row = row + [""] * (len(headers) - len(row))
        row = row[: len(headers)]

        record = {
            headers[i]: (row[i].strip() if i < len(row) else "")
            for i in range(len(headers))
            if headers[i]
        }

        movement_type = record.get("movement_type", "").strip()
        movement_date = record.get("date", "").strip()
        site_value = record.get("site_logging_movement", "").strip()

        # Skip explanatory/instruction rows above and below table data.
        if not movement_type and not movement_date:
            continue
        if site_value.upper() in {"FORMULA", "SITE LOGGING MOVEMENT"}:
            continue

        records.append(_record_with_source_key(record))

    return records


def find_header_index(rows: list[list[str]]) -> int:
    for idx, row in enumerate(rows):
        non_empty = {cell.strip().upper() for cell in row if cell.strip()}
        if HEADER_SENTINELS.issubset(non_empty):
            return idx
    raise ValueError("Could not locate asset movement header row")


def parse_asset_log_csv(path: str) -> list[dict]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))

    return normalize_matrix_rows(rows)


def parse_movement_date(value: str | None):
    if not value:
        return None

    for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None
