from datetime import UTC, datetime

from app.extensions import db
from app.models import AssetMovement
from app.services.parsing import parse_movement_date


def upsert_asset_rows(rows: list[dict]) -> dict[str, int]:
    inserted = 0
    updated = 0

    for row in rows:
        source_key = row.get("_source_key")
        if not source_key:
            continue

        existing = AssetMovement.query.filter_by(source_key=source_key).one_or_none()
        if existing is None:
            record = AssetMovement(
                source_key=source_key,
                site_logging_movement=row.get("site_logging_movement"),
                movement_date=parse_movement_date(row.get("date")),
                movement_type=row.get("movement_type"),
                bin_value=row.get("bin"),
                item_number=row.get("item"),
                asset_type=row.get("asset_type"),
                owned_by=row.get("owned_by"),
                payload=row,
                ingested_at=datetime.now(UTC),
            )
            db.session.add(record)
            inserted += 1
        else:
            existing.site_logging_movement = row.get("site_logging_movement")
            existing.movement_date = parse_movement_date(row.get("date"))
            existing.movement_type = row.get("movement_type")
            existing.bin_value = row.get("bin")
            existing.item_number = row.get("item")
            existing.asset_type = row.get("asset_type")
            existing.owned_by = row.get("owned_by")
            existing.payload = row
            existing.ingested_at = datetime.now(UTC)
            updated += 1

    db.session.commit()
    return {"inserted": inserted, "updated": updated, "total": inserted + updated}
