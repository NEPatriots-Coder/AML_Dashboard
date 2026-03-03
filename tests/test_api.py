from pathlib import Path

from app import create_app
from app.config import Config
from app.extensions import db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    ASSET_LOG_CSV_PATH = str(Path("tests/fixtures/sample_asset_log.csv"))
    ENABLE_BACKGROUND_SYNC = False


def test_health_endpoint():
    app = create_app(TestConfig)
    client = app.test_client()

    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_source_check_endpoint_csv_mode():
    app = create_app(TestConfig)
    client = app.test_client()

    response = client.get("/api/source/check")
    assert response.status_code == 200
    body = response.get_json()
    assert body["ok"] is True
    assert body["source"] == "csv"
    assert body["source_count"] == 2


def test_live_and_sync_and_db_query_endpoints():
    app = create_app(TestConfig)
    client = app.test_client()

    with app.app_context():
        db.drop_all()
        db.create_all()

    live = client.get("/api/assets/live?bin=storage")
    assert live.status_code == 200
    assert live.get_json()["count"] == 1

    sync = client.post("/api/assets/sync")
    assert sync.status_code == 200
    assert sync.get_json()["synced"]["total"] == 2

    query = client.get("/api/assets?q=vendor")
    assert query.status_code == 200
    assert query.get_json()["count"] >= 1


def test_live_endpoint_pagination_metadata():
    app = create_app(TestConfig)
    client = app.test_client()

    response = client.get("/api/assets/live?limit=1&offset=0&sort_by=date&sort_dir=asc")
    assert response.status_code == 200
    body = response.get_json()
    assert body["limit"] == 1
    assert body["offset"] == 0
    assert body["sort_by"] == "date"
    assert body["sort_dir"] == "asc"
    assert body["total"] >= body["count"]


def test_live_endpoint_multi_value_filter():
    app = create_app(TestConfig)
    client = app.test_client()

    response = client.get("/api/assets/live?item=nonexistent&item=EAB-1002")
    assert response.status_code == 200
    body = response.get_json()
    assert body["count"] == 1


def test_live_export_csv_and_html():
    app = create_app(TestConfig)
    client = app.test_client()

    csv_res = client.get("/api/assets/live/export.csv?bin=storage")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.content_type
    assert "attachment; filename=" in csv_res.headers.get("Content-Disposition", "")
    assert "bin" in csv_res.get_data(as_text=True).lower()

    html_res = client.get("/api/assets/live/export.html?bin=storage")
    assert html_res.status_code == 200
    assert "text/html" in html_res.content_type
    assert "attachment; filename=" in html_res.headers.get("Content-Disposition", "")
    html_body = html_res.get_data(as_text=True).lower()
    assert "<table>" in html_body
    assert "asset search results" in html_body
