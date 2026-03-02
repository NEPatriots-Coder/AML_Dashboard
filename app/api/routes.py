from flask import Blueprint, current_app, jsonify, request

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

        filters = {
            k: v
            for k, v in request.args.items()
            if k not in QUERY_META_KEYS and v is not None and v != ""
        }

        cache_key = "live_rows"
        rows = None if force_refresh else runtime_cache.get(cache_key) if runtime_cache else None
        if rows is None:
            rows = get_live_rows(current_app.config)
            if runtime_cache:
                runtime_cache.set(cache_key, rows)

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
    query = request.args.get("q", "").strip().lower()

    filters = {
        k: v
        for k, v in request.args.items()
        if k not in QUERY_META_KEYS and v is not None and v != ""
    }

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
