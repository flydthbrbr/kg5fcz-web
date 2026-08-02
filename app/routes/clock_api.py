from datetime import datetime, timezone

from flask import Blueprint, request
from flask_login import current_user

from app.extensions import db
from app.models import User
from app.services.api_tokens import verify_api_token
from app.services.clock_settings import (
    get_or_create_clock_settings,
)


clock_api = Blueprint(
    "clock_api",
    __name__,
    url_prefix="/api/v1/account",
)


def bearer_token_from_request() -> str | None:
    """Extract a Bearer credential from the Authorization header."""

    authorization = request.headers.get(
        "Authorization",
        "",
    ).strip()

    if not authorization:
        return None

    scheme, separator, credentials = authorization.partition(" ")

    if (
        not separator
        or scheme.lower() != "bearer"
        or not credentials.strip()
    ):
        return None

    return credentials.strip()


def resolve_clock_user() -> User | None:
    """
    Resolve the API user from a browser session or Bearer token.

    Browser-session authentication takes precedence.
    """

    if current_user.is_authenticated:
        return current_user

    raw_token = bearer_token_from_request()

    if raw_token is None:
        return None

    token_record = verify_api_token(
        raw_token,
        required_scope="clock:read",
    )

    if token_record is None:
        return None

    # verify_api_token() updates last_used_at but intentionally does
    # not commit. The API request owns the transaction boundary.
    db.session.commit()

    return token_record.user


def build_clock_payload(user: User) -> dict:
    """Build the versioned OpenHamClock configuration document."""

    profile = user.profile
    station = user.station
    settings = get_or_create_clock_settings(user)

    grid_square = None

    if station and station.grid_square:
        grid_square = station.grid_square
    elif profile and profile.grid_square:
        grid_square = profile.grid_square

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authenticated": True,
        "operator": {
            "user_id": user.id,
            "callsign": user.callsign,
            "display_name": (
                profile.display_name
                if profile
                else None
            ),
            "timezone": (
                profile.timezone
                if profile
                else "UTC"
            ),
        },
        "station": {
            "configured": station is not None,
            "station_name": (
                station.station_name
                if station
                else None
            ),
            "grid_square": grid_square,
            "dxcc_entity": (
                station.dxcc_entity
                if station
                else None
            ),
            "primary_rig": (
                station.primary_rig
                if station
                else None
            ),
            "primary_antenna": (
                station.primary_antenna
                if station
                else None
            ),
        },
        "clock": {
            "theme": settings.theme,
            "units": settings.units,
            "map_projection": settings.map_projection,
            "show_satellites": settings.show_satellites,
            "show_dx_cluster": settings.show_dx_cluster,
            "show_weather": settings.show_weather,
            "show_moon": settings.show_moon,
            "show_grayline": settings.show_grayline,
            "default_zoom": settings.default_zoom,
        },
    }


@clock_api.get("/clock")
def clock_configuration():
    """Return OpenHamClock settings using session or token auth."""

    user = resolve_clock_user()

    if user is None:
        return {
            "authenticated": False,
            "error": "Authentication required.",
        }, 401

    return build_clock_payload(user), 200
