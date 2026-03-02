from pathlib import Path

from app.services.parsing import parse_asset_log_csv


def test_parse_asset_log_csv_detects_header_and_rows():
    csv_path = Path("tests/fixtures/sample_asset_log.csv")
    rows = parse_asset_log_csv(str(csv_path))

    assert len(rows) == 2
    assert rows[0]["movement_type"] == "RECEIVED"
    assert rows[0]["bin"] == "STORAGE"
    assert "_source_key" in rows[0]
