from datetime import datetime, timezone

from app.extensions import db


class Station(db.Model):
    __tablename__ = "stations"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    station_name = db.Column(
        db.String(100),
        nullable=False,
        default="Home Station",
    )

    grid_square = db.Column(db.String(8), nullable=True)
    primary_rig = db.Column(db.String(100), nullable=True)
    primary_antenna = db.Column(db.String(150), nullable=True)
    license_class = db.Column(db.String(30), nullable=True)
    dxcc_entity = db.Column(db.String(100), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship(
        "User",
        back_populates="station",
    )
