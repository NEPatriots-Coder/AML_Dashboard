import logging

from app.services.google_sheets import fetch_rows_from_google_sheet
from app.services.parsing import parse_asset_log_csv

logger = logging.getLogger(__name__)


def get_live_rows_with_meta(config) -> tuple[list[dict], str, str | None]:
    source = str(config.get("SHEET_SOURCE", "csv")).lower()

    if source == "google":
        try:
            rows = fetch_rows_from_google_sheet(
                sheet_id=config.get("GOOGLE_SHEET_ID", ""),
                worksheet_name=config.get("GOOGLE_SHEET_NAME", "ASSET MVMT LOG"),
                worksheet_gid=config.get("GOOGLE_SHEET_GID", ""),
                service_account_file=config.get("GOOGLE_SERVICE_ACCOUNT_FILE", ""),
                oauth_client_secret_file=config.get("GOOGLE_OAUTH_CLIENT_SECRET_FILE", ""),
                oauth_token_file=config.get("GOOGLE_OAUTH_TOKEN_FILE", ""),
                oauth_interactive=bool(config.get("GOOGLE_OAUTH_INTERACTIVE", False)),
            )
            return rows, "google", None
        except Exception as exc:
            fallback_mode = str(config.get("SHEET_SOURCE_FALLBACK", "csv")).lower()
            if fallback_mode != "csv":
                raise
            logger.warning("Google Sheets fetch failed, falling back to CSV: %s", exc)
            rows = parse_asset_log_csv(str(config.get("ASSET_LOG_CSV_PATH", "")))
            return rows, "csv_fallback", str(exc)

    if source == "csv":
        rows = parse_asset_log_csv(str(config.get("ASSET_LOG_CSV_PATH", "")))
        return rows, "csv", None

    raise ValueError(f"Unsupported SHEET_SOURCE: {source}")


def get_live_rows(config) -> list[dict]:
    rows, _, _ = get_live_rows_with_meta(config)
    return rows
