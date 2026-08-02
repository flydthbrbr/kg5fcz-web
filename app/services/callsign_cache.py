from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

from flask import current_app

from app.extensions import db
from app.models import CallsignLookup
from app.services.callsign import (
    CallsignRecord,
    lookup_callsign,
    normalize_callsign,
)


def utc_now() -> datetime:
    """Return the current timezone-aware UTC time."""

    return datetime.now(timezone.utc)


def as_aware_utc(value: datetime) -> datetime:
    """Normalize SQLite timestamps to timezone-aware UTC."""

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def cache_success_ttl() -> timedelta:
    days = int(
        current_app.config.get(
            "CALLSIGN_CACHE_SUCCESS_DAYS",
            7,
        )
    )
    return timedelta(days=days)


def cache_not_found_ttl() -> timedelta:
    hours = int(
        current_app.config.get(
            "CALLSIGN_CACHE_NOT_FOUND_HOURS",
            24,
        )
    )
    return timedelta(hours=hours)


def get_cached_lookup(callsign: str) -> CallsignLookup | None:
    normalized = normalize_callsign(callsign)

    return db.session.scalar(
        db.select(CallsignLookup).where(
            CallsignLookup.callsign == normalized
        )
    )


def cache_to_record(
    cached: CallsignLookup,
    *,
    stale: bool = False,
) -> CallsignRecord | None:
    if not cached.found:
        return None

    return CallsignRecord(
        callsign=cached.callsign,
        display_name=cached.display_name,
        grid_square=cached.grid_square,
        dxcc_entity=cached.dxcc_entity,
        cq_zone=cached.cq_zone,
        itu_zone=cached.itu_zone,
        provider=cached.provider,
        looked_up_at=as_aware_utc(cached.looked_up_at),
        from_cache=True,
        stale=stale,
    )


def save_lookup_result(
    callsign: str,
    record: CallsignRecord | None,
) -> CallsignLookup:
    normalized = normalize_callsign(callsign)
    now = utc_now()

    cached = get_cached_lookup(normalized)

    if cached is None:
        cached = CallsignLookup(callsign=normalized)

    if record is None:
        cached.display_name = None
        cached.grid_square = None
        cached.dxcc_entity = None
        cached.cq_zone = None
        cached.itu_zone = None
        cached.provider = "unknown"
        cached.found = False
        cached.looked_up_at = now
        cached.expires_at = now + cache_not_found_ttl()
        cached.raw_response_json = None
    else:
        cached.display_name = record.display_name
        cached.grid_square = record.grid_square
        cached.dxcc_entity = record.dxcc_entity
        cached.cq_zone = record.cq_zone
        cached.itu_zone = record.itu_zone
        cached.provider = record.provider or "unknown"
        cached.found = True
        cached.looked_up_at = now
        cached.expires_at = now + cache_success_ttl()
        cached.raw_response_json = None

    db.session.add(cached)
    db.session.commit()

    return cached


def lookup_callsign_cached(
    callsign: str,
    *,
    force_refresh: bool = False,
) -> CallsignRecord | None:
    normalized = normalize_callsign(callsign)

    if not normalized:
        return None

    cached = get_cached_lookup(normalized)
    now = utc_now()

    if cached is not None and not force_refresh:
        expires_at = as_aware_utc(cached.expires_at)

        if expires_at > now:
            return cache_to_record(cached)

    try:
        provider_record = lookup_callsign(normalized)
    except Exception:
        current_app.logger.exception(
            "Callsign lookup failed for %s",
            normalized,
        )

        if cached is not None and cached.found:
            return cache_to_record(
                cached,
                stale=True,
            )

        raise

    saved = save_lookup_result(
        normalized,
        provider_record,
    )

    if provider_record is None:
        return None

    return replace(
        provider_record,
        looked_up_at=as_aware_utc(saved.looked_up_at),
        from_cache=False,
        stale=False,
    )
