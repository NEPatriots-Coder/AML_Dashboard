# AML Dashboard (Phase 1+)

Backend + frontend foundation for ingesting Asset Movement Log data, backing it up to Postgres, and exposing searchable APIs with a dashboard UI.

## Backend quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

## Frontend quick start

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://127.0.0.1:5180` and proxies API calls to the Flask server.

## Backend API endpoints

- `GET /api/health`
- `GET /api/source/check`
- `GET /api/assets/live`
- Query params for `GET /api/assets/live` and `GET /api/assets`:
  - Filters: `q`, `bin`, `movement_type`, any column key
  - Cache: `refresh=true` (live endpoint only)
  - Pagination: `limit`, `offset`
  - Sorting: `sort_by`, `sort_dir` (`asc` or `desc`)
- `POST /api/assets/sync`
- `GET /api/assets`

Response metadata includes `count`, `total`, `limit`, `offset`, `sort_by`, `sort_dir`.

## Google auth modes

### Option A: Service account (recommended)

1. Put service account key at `secrets/service-account.json`.
2. Share the sheet with the service account email as Viewer.
3. Keep `SHEET_SOURCE=google`.

### Option B: OAuth installed-app (uses your OAuth client JSON)

1. Put OAuth client JSON at `secrets/oauth_client.json`.
2. Generate token once:

```bash
source .venv/bin/activate
python scripts/google_oauth_bootstrap.py
```

3. This writes `secrets/oauth_token.json`.
4. Ensure `.env` has:

```env
GOOGLE_OAUTH_CLIENT_SECRET_FILE=./secrets/oauth_client.json
GOOGLE_OAUTH_TOKEN_FILE=./secrets/oauth_token.json
GOOGLE_OAUTH_INTERACTIVE=false
```

## Backend tests

```bash
pytest -q
```

## Docker Compose

```bash
docker compose up --build
```

Services:
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5180`
- Postgres: `localhost:5434`
