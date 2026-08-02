from datetime import datetime, timezone

from app.extensions import db


class ClockSettings(db.Model):
    """Per-user display preferences for OpenHamClock."""

    __tablename__ = "clock_settings"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    theme = db.Column(
        db.String(20),
        nullable=False,
        default="dark",
    )

    units = db.Column(
        db.String(20),
        nullable=False,
        default="imperial",
    )

    map_projection = db.Column(
        db.String(30),
        nullable=False,
        default="mercator",
    )

    show_satellites = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    show_dx_cluster = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    show_weather = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    show_moon = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    show_grayline = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    default_zoom = db.Column(
        db.Integer,
        nullable=False,
        default=2,
    )

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
        back_populates="clock_settings",
    )

    def __repr__(self) -> str:
        return (
            f"<ClockSettings user_id={self.user_id} "
            f"theme={self.theme!r}>"
        )
