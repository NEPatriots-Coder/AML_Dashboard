import logging
import threading
import time

from flask import Flask

from app.api import api
from app.config import Config
from app.extensions import db
from app.services import get_live_rows, upsert_asset_rows
from app.services.runtime import init_runtime_cache


def _start_background_sync(app: Flask) -> None:
    def run_loop() -> None:
        interval = app.config["SYNC_INTERVAL_SECONDS"]
        while True:
            with app.app_context():
                try:
                    rows = get_live_rows(app.config)
                    upsert_asset_rows(rows)
                except Exception as exc:  # pragma: no cover
                    app.logger.exception("Background sync failed: %s", exc)
            time.sleep(interval)

    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()


def create_app(config_object=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    logging.basicConfig(level=logging.INFO)

    db.init_app(app)
    init_runtime_cache(app.config["CACHE_TTL_SECONDS"])

    with app.app_context():
        db.create_all()

        # Initial sync on startup keeps Postgres backup as fresh as possible.
        try:
            rows = get_live_rows(app.config)
            upsert_asset_rows(rows)
            app.logger.info("Startup sync complete with %d source rows", len(rows))
        except Exception as exc:  # pragma: no cover
            app.logger.warning("Startup sync skipped due to error: %s", exc)

    app.register_blueprint(api)

    if app.config["ENABLE_BACKGROUND_SYNC"]:
        _start_background_sync(app)

    return app
