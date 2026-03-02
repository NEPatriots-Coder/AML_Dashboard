from pathlib import Path

from app import create_app
from app.config import Config
from app.extensions import db
from app.models import AssetMovement
from app.services.parsing import parse_asset_log_csv
from app.services.sync import upsert_asset_rows


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    ASSET_LOG_CSV_PATH = str(Path("tests/fixtures/sample_asset_log.csv"))
    ENABLE_BACKGROUND_SYNC = False


def test_upsert_asset_rows_inserts_and_updates():
    app = create_app(TestConfig)

    with app.app_context():
        db.drop_all()
        db.create_all()

        rows = parse_asset_log_csv(TestConfig.ASSET_LOG_CSV_PATH)
        first = upsert_asset_rows(rows)
        second = upsert_asset_rows(rows)

        assert first["inserted"] == 2
        assert second["updated"] == 2
        assert AssetMovement.query.count() == 2
