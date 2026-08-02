from datetime import datetime, timezone

from app.extensions import db


class ApiToken(db.Model):
    """Revocable API credential belonging to one user."""

    __tablename__ = "api_tokens"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = db.Column(
        db.String(100),
        nullable=False,
        default="OpenHamClock",
    )

    token_hash = db.Column(
        db.String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    token_prefix = db.Column(
        db.String(16),
        nullable=False,
        index=True,
    )

    scope = db.Column(
        db.String(100),
        nullable=False,
        default="clock:read",
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    last_used_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    revoked_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    user = db.relationship(
        "User",
        back_populates="api_tokens",
    )

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def __repr__(self) -> str:
        return (
            f"<ApiToken id={self.id} "
            f"user_id={self.user_id} "
            f"prefix={self.token_prefix!r}>"
        )
