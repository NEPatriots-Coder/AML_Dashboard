import csv
import io
from datetime import UTC, datetime
from html import escape

from flask import Blueprint, Response, current_app, jsonify, request

from app.models import AssetMovement
from app.services import apply_filters, get_live_rows, get_live_rows_with_meta, upsert_asset_rows
from app.services.parsing import parse_movement_date
from app.services.runtime import runtime_cache

api = Blueprint("api", __name__, url_prefix="/api")

QUERY_META_KEYS = {"q", "refresh", "limit", "offset", "sort_by", "sort_dir"}


def _parse_query_meta() -> tuple[int, int, str, str]:
    try:
        limit = int(request.args.get("limit", "100"))
    except ValueError:
        limit = 100
    try:
        offset = int(request.args.get("offset", "0"))
    except ValueError:
        offset = 0

    limit = min(max(limit, 1), 1000)
    offset = max(offset, 0)

    sort_by = request.args.get("sort_by", "date").strip().lower() or "date"
    sort_dir = request.args.get("sort_dir", "desc").strip().lower()
    if sort_dir not in {"asc", "desc"}:
        sort_dir = "desc"

    return limit, offset, sort_by, sort_dir


def _sort_rows(rows: list[dict], sort_by: str, sort_dir: str) -> list[dict]:
    reverse = sort_dir == "desc"

    if sort_by in {"date", "_movement_date"}:
        def date_key(row: dict):
            value = parse_movement_date(str(row.get("date") or row.get("_movement_date") or ""))
            return value.isoformat() if value else ""

        return sorted(rows, key=date_key, reverse=reverse)

    def text_key(row: dict):
        value = row.get(sort_by)
        if value is None:
            return ""
        return str(value).lower()

    return sorted(rows, key=text_key, reverse=reverse)


def _paginate_rows(rows: list[dict], limit: int, offset: int) -> list[dict]:
    return rows[offset : offset + limit]


def _split_filter_terms(values: list[str]) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for raw_value in values:
        if raw_value is None:
            continue
        for piece in raw_value.split(","):
            value = piece.strip()
            if not value:
                continue
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            terms.append(value)
    return terms


def _parse_filters() -> dict[str, list[str]]:
    filters: dict[str, list[str]] = {}
    for key in request.args.keys():
        if key in QUERY_META_KEYS:
            continue
        values = _split_filter_terms(request.args.getlist(key))
        if values:
            filters[key] = values
    return filters


def _get_live_rows_from_cache(force_refresh: bool) -> list[dict]:
    cache_key = "live_rows"
    rows = None if force_refresh else runtime_cache.get(cache_key) if runtime_cache else None
    if rows is None:
        rows = get_live_rows(current_app.config)
        if runtime_cache:
            runtime_cache.set(cache_key, rows)
    return rows


def _select_rows_for_query(source: str) -> list[dict]:
    force_refresh = request.args.get("refresh", "false").lower() == "true"
    query = request.args.get("q")
    filters = _parse_filters()

    if source == "live":
        rows = _get_live_rows_from_cache(force_refresh=force_refresh)
    else:
        rows = [rec.to_dict() for rec in AssetMovement.query.all()]

    filtered = apply_filters(rows, filters=filters, global_query=query)
    _, _, sort_by, sort_dir = _parse_query_meta()
    return _sort_rows(filtered, sort_by=sort_by, sort_dir=sort_dir)


def _derive_headers(rows: list[dict]) -> list[str]:
    headers: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key in seen:
                continue
            seen.add(key)
            headers.append(key)
    return headers


def _build_download_filename(extension: str) -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return f"asset-search-{timestamp}.{extension}"


def _rows_to_csv_response(rows: list[dict]) -> Response:
    headers = _derive_headers(rows)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, extrasaction="ignore")
    if headers:
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{_build_download_filename("csv")}"',
            "Cache-Control": "no-store",
        },
    )


def _rows_to_html_response(rows: list[dict]) -> Response:
    headers = _derive_headers(rows)
    columns = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{escape(str(row.get(header, '')))}</td>" for header in headers)
        body_rows.append(f"<tr>{cells}</tr>")
    html_body = "".join(body_rows)
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Asset Search Results</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #1f2937; }}
    h1 {{ margin: 0 0 8px 0; }}
    p {{ margin: 0 0 16px 0; color: #6b7280; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 6px 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; position: sticky; top: 0; }}
    tr:nth-child(even) {{ background: #f9fafb; }}
  </style>
</head>
<body>
  <h1>Asset Search Results</h1>
  <p>Exported {escape(datetime.now(UTC).isoformat())} · Rows: {len(rows)}</p>
  <table>
    <thead><tr>{columns}</tr></thead>
    <tbody>{html_body}</tbody>
  </table>
</body>
</html>"""
    return Response(
        html,
        mimetype="text/html",
        headers={
            "Content-Disposition": f'attachment; filename="{_build_download_filename("html")}"',
            "Cache-Control": "no-store",
        },
    )


@api.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@api.get("/source/check")
def check_source():
    cfg = current_app.config
    payload = {"source": cfg.get("SHEET_SOURCE", "unknown"), "ok": False}
    try:
        rows, source_mode, fallback_reason = get_live_rows_with_meta(cfg)
        payload["source_count"] = len(rows)
        payload["source_mode"] = source_mode
        payload["using_fallback"] = source_mode == "csv_fallback"
        if fallback_reason:
            payload["fallback_reason"] = fallback_reason
        payload["ok"] = True
    except Exception as exc:
        payload["error"] = str(exc)
        return jsonify(payload), 503
    return jsonify(payload), 200


@api.get("/assets/live")
def live_assets():
    try:
        limit, offset, sort_by, sort_dir = _parse_query_meta()
        force_refresh = request.args.get("refresh", "false").lower() == "true"
        query = request.args.get("q")
        filters = _parse_filters()

        rows = _get_live_rows_from_cache(force_refresh=force_refresh)
        filtered = apply_filters(rows, filters=filters, global_query=query)
        sorted_rows = _sort_rows(filtered, sort_by=sort_by, sort_dir=sort_dir)
        page_rows = _paginate_rows(sorted_rows, limit=limit, offset=offset)
        return jsonify(
            {
                "count": len(page_rows),
                "total": len(sorted_rows),
                "offset": offset,
                "limit": limit,
                "sort_by": sort_by,
                "sort_dir": sort_dir,
                "rows": page_rows,
            }
        )
    except Exception as exc:
        current_app.logger.exception("Live asset query failed: %s", exc)
        return jsonify({"error": str(exc), "ok": False}), 503


@api.get("/assets/live/export.csv")
def export_live_assets_csv():
    rows = _select_rows_for_query("live")
    return _rows_to_csv_response(rows)


@api.get("/assets/live/export.html")
def export_live_assets_html():
    rows = _select_rows_for_query("live")
    return _rows_to_html_response(rows)


@api.post("/assets/sync")
def sync_assets():
    rows = get_live_rows(current_app.config)
    stats = upsert_asset_rows(rows)
    if runtime_cache:
        runtime_cache.set("live_rows", rows)
    return jsonify({"synced": stats, "source_count": len(rows)})


@api.get("/assets")
def db_assets():
    limit, offset, sort_by, sort_dir = _parse_query_meta()
    query = request.args.get("q")
    filters = _parse_filters()

    rows = [rec.to_dict() for rec in AssetMovement.query.all()]
    filtered = apply_filters(rows, filters=filters, global_query=query)
    sorted_rows = _sort_rows(filtered, sort_by=sort_by, sort_dir=sort_dir)
    page_rows = _paginate_rows(sorted_rows, limit=limit, offset=offset)
    return jsonify(
        {
            "count": len(page_rows),
            "total": len(sorted_rows),
            "offset": offset,
            "limit": limit,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
            "rows": page_rows,
        }
    )
