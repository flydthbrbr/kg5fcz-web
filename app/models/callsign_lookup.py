from datetime import datetime, timezone

from app.extensions import db


class CallsignLookup(db.Model):
    __tablename__ = "callsign_lookups"

    id = db.Column(db.Integer, primary_key=True)

    callsign = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
        index=True,
    )

    display_name = db.Column(db.String(150))
    grid_square = db.Column(db.String(8))
    dxcc_entity = db.Column(db.String(100))
    cq_zone = db.Column(db.Integer)
    itu_zone = db.Column(db.Integer)

    provider = db.Column(
        db.String(50),
        nullable=False,
    )

    found = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    looked_up_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    expires_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
    )

    raw_response_json = db.Column(db.Text)
