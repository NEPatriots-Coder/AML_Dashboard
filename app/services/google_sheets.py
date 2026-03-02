from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from app.services.parsing import normalize_matrix_rows


def _resolve_range_for_gid(service, spreadsheet_id: str, worksheet_gid: str) -> str:
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = spreadsheet.get("sheets", [])
    for sheet in sheets:
        properties = sheet.get("properties", {})
        if str(properties.get("sheetId")) == str(worksheet_gid):
            return properties.get("title", "")
    raise ValueError(f"Could not resolve worksheet title for gid={worksheet_gid}")


def _extract_gid_from_name_or_url(worksheet_name_or_url: str) -> str | None:
    value = (worksheet_name_or_url or "").strip()
    if not value:
        return None

    if value.isdigit():
        return value

    match = re.search(r"(?:gid=)(\d+)", value)
    if match:
        return match.group(1)

    return None


def fetch_rows_from_google_sheet(
    *,
    sheet_id: str,
    worksheet_name: str,
    worksheet_gid: str,
    service_account_file: str,
    oauth_client_secret_file: str,
    oauth_token_file: str,
    oauth_interactive: bool,
) -> list[dict[str, Any]]:
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials as UserCredentials
        from google.oauth2.service_account import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Google dependencies are not installed. Install google-api-python-client, google-auth, and google-auth-oauthlib."
        ) from exc

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    creds = None
    sa_path = Path(service_account_file) if service_account_file else None
    oauth_client_path = Path(oauth_client_secret_file) if oauth_client_secret_file else None
    oauth_token_path = Path(oauth_token_file) if oauth_token_file else None

    if sa_path and sa_path.exists():
        creds = Credentials.from_service_account_file(str(sa_path), scopes=scopes)
    elif oauth_client_path and oauth_client_path.exists():
        if oauth_token_path and oauth_token_path.exists():
            creds = UserCredentials.from_authorized_user_file(str(oauth_token_path), scopes=scopes)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        if creds is None or not creds.valid:
            if not oauth_interactive:
                raise RuntimeError(
                    "OAuth token missing/invalid and GOOGLE_OAUTH_INTERACTIVE is false. "
                    "Generate token via scripts/google_oauth_bootstrap.py or enable interactive mode."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(oauth_client_path), scopes=scopes)
            creds = flow.run_local_server(port=0)
            if oauth_token_path:
                oauth_token_path.parent.mkdir(parents=True, exist_ok=True)
                oauth_token_path.write_text(creds.to_json(), encoding="utf-8")
    else:
        raise RuntimeError(
            "No Google credentials found. Provide GOOGLE_SERVICE_ACCOUNT_FILE or GOOGLE_OAUTH_CLIENT_SECRET_FILE."
        )

    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    resolved_gid = worksheet_gid or _extract_gid_from_name_or_url(worksheet_name)
    worksheet_range = worksheet_name
    if resolved_gid:
        worksheet_range = _resolve_range_for_gid(service, sheet_id, resolved_gid)

    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=worksheet_range)
        .execute()
    )

    values = result.get("values", [])
    return normalize_matrix_rows(values)
