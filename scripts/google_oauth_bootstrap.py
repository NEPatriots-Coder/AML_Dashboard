from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def main() -> None:
    secrets_path = Path("secrets/oauth_client.json")
    token_path = Path("secrets/oauth_token.json")

    if not secrets_path.exists():
        raise SystemExit(
            "Missing OAuth client file at secrets/oauth_client.json. "
            "Put your installed-app OAuth JSON there first."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    print(f"Wrote OAuth token to {token_path}")


if __name__ == "__main__":
    main()
