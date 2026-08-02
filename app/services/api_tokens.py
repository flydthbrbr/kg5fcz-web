from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timezone

from app.extensions import db
from app.models import ApiToken, User


TOKEN_PREFIX_LENGTH = 12
TOKEN_BYTES = 32
DEFAULT_SCOPE = "clock:read"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hash_token(raw_token: str) -> str:
    """Return the SHA-256 hex digest for a raw API token."""

    return hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()


def token_prefix(raw_token: str) -> str:
    """Return the non-secret prefix used to narrow token searches."""

    return raw_token[:TOKEN_PREFIX_LENGTH]


def generate_api_token(
    user: User,
    *,
    name: str = "OpenHamClock",
    scope: str = DEFAULT_SCOPE,
) -> tuple[ApiToken, str]:
    """
    Generate and stage a new API token.

    The raw token is returned once. Only its hash is stored.
    The caller controls the database commit.
    """

    raw_token = secrets.token_urlsafe(TOKEN_BYTES)

    record = ApiToken(
        user=user,
        name=name.strip() or "OpenHamClock",
        token_hash=hash_token(raw_token),
        token_prefix=token_prefix(raw_token),
        scope=scope,
    )

    db.session.add(record)

    return record, raw_token


def verify_api_token(
    raw_token: str,
    *,
    required_scope: str | None = None,
    update_last_used: bool = True,
) -> ApiToken | None:
    """
    Verify a raw token and return its active database record.

    Revoked tokens and tokens lacking the required scope are rejected.
    """

    if not raw_token:
        return None

    prefix = token_prefix(raw_token)

    candidates = db.session.scalars(
        db.select(ApiToken).where(
            ApiToken.token_prefix == prefix,
            ApiToken.revoked_at.is_(None),
        )
    ).all()

    candidate_hash = hash_token(raw_token)

    for record in candidates:
        if not hmac.compare_digest(
            record.token_hash,
            candidate_hash,
        ):
            continue

        if required_scope and record.scope != required_scope:
            return None

        if update_last_used:
            record.last_used_at = utc_now()
            db.session.add(record)

        return record

    return None


def revoke_api_token(record: ApiToken) -> None:
    """Mark an API token as revoked without deleting its audit record."""

    if record.revoked_at is None:
        record.revoked_at = utc_now()
        db.session.add(record)
