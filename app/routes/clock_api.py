from datetime import datetime, timezone

from flask import Blueprint
from flask_login import current_user

from app.services.clock_settings import (
    get_or_create_clock_settings,
)


clock_api = Blueprint(
    "clock_api",
    __name__,
    url_prefix="/api/v1/account",
)


@clock_api.get("/clock")
def clock_configuration():
    """Return normalized OpenHamClock settings for the current user."""

    if not current_user.is_authenticated:
        return {
            "authenticated": False,
            "error": "Authentication required.",
        }, 401

    profile = current_user.profile
    station = current_user.station
    settings = get_or_create_clock_settings(current_user)

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
            "user_id": current_user.id,
            "callsign": current_user.callsign,
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
    }, 200
