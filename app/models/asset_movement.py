from datetime import UTC, date, datetime

from app.extensions import db


class AssetMovement(db.Model):
    __tablename__ = "asset_movements"

    id = db.Column(db.Integer, primary_key=True)
    source_key = db.Column(db.String(64), unique=True, nullable=False, index=True)

    site_logging_movement = db.Column(db.String(128), nullable=True, index=True)
    movement_date = db.Column(db.Date, nullable=True, index=True)
    movement_type = db.Column(db.String(64), nullable=True, index=True)
    bin_value = db.Column(db.String(128), nullable=True, index=True)
    item_number = db.Column(db.String(128), nullable=True, index=True)
    asset_type = db.Column(db.String(128), nullable=True, index=True)
    owned_by = db.Column(db.String(64), nullable=True, index=True)

    payload = db.Column(db.JSON, nullable=False)
    ingested_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        data = dict(self.payload)
        data["_source_key"] = self.source_key
        data["_ingested_at"] = self.ingested_at.isoformat()
        if isinstance(self.movement_date, date):
            data["_movement_date"] = self.movement_date.isoformat()
        return data
