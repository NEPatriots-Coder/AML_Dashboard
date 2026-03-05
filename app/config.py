import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_path(value: str | None, *, default: Path | None = None) -> str:
    raw = (value or "").strip()
    if not raw:
        if default is None:
            return ""
        path = default
    else:
        path = Path(raw).expanduser()
    if not path.is_absolute():
        path = BASE_DIR / path
    return str(path.resolve())


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///asset_dashboard.db")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))

    SHEET_SOURCE = os.getenv("SHEET_SOURCE", "csv")
    ASSET_LOG_CSV_PATH = _resolve_path(
        os.getenv("ASSET_LOG_CSV_PATH"),
        default=BASE_DIR / "US-LZL01 - ASSET MVMT LOG - ASSET MVMT LOG.csv",
    )

    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
    GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "ASSET MVMT LOG")
    GOOGLE_SHEET_GID = os.getenv("GOOGLE_SHEET_GID", "")
    GOOGLE_SERVICE_ACCOUNT_FILE = _resolve_path(os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"))
    GOOGLE_OAUTH_CLIENT_SECRET_FILE = _resolve_path(os.getenv("GOOGLE_OAUTH_CLIENT_SECRET_FILE"))
    GOOGLE_OAUTH_TOKEN_FILE = _resolve_path(os.getenv("GOOGLE_OAUTH_TOKEN_FILE"))
    GOOGLE_OAUTH_INTERACTIVE = os.getenv("GOOGLE_OAUTH_INTERACTIVE", "false").lower() == "true"
    SHEET_SOURCE_FALLBACK = os.getenv("SHEET_SOURCE_FALLBACK", "csv")

    ENABLE_BACKGROUND_SYNC = os.getenv("ENABLE_BACKGROUND_SYNC", "true").lower() == "true"
    SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", "60"))
