# AML Dashboard Frontend

Tron-inspired React + TypeScript + Tailwind dashboard shell for querying the Flask asset APIs.

## Run

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api/*` calls to `http://127.0.0.1:8000`.

## Primary screen

- Corporate logo header with source telemetry status.
- Summary cards for visible rows and key aggregates.
- Filter bar for global query, BIN filter, movement-type filter.
- Server-side pagination and sorting controls.
- Scrollable data table with sticky header.
- Clickable row inspector panel for full record details.
