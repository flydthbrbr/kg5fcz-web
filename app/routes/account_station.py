from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import StationForm
from app.models import Station
from app.services.callsign import lookup_callsign

station_account = Blueprint("station_account", __name__)


def clean_optional(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()
    return cleaned or None


@station_account.route("/account/station", methods=["GET", "POST"])
@login_required
def edit_station():
    station = current_user.station

    if station is None:
        station = Station(
            user=current_user,
            station_name="Home Station",
        )

    form = StationForm(obj=station)

    if form.validate_on_submit():
        station.station_name = (
            clean_optional(form.station_name.data)
            or "Home Station"
        )

        grid_square = clean_optional(form.grid_square.data)
        station.grid_square = grid_square.upper() if grid_square else None

        station.primary_rig = clean_optional(form.primary_rig.data)
        station.primary_antenna = clean_optional(
            form.primary_antenna.data
        )
        station.license_class = clean_optional(
            form.license_class.data
        )
        station.dxcc_entity = clean_optional(
            form.dxcc_entity.data
        )

        db.session.add(station)
        db.session.commit()

        flash(
            "Your station information has been updated.",
            "success",
        )

        return redirect(
            url_for("station_account.edit_station")
        )

    return render_template(
        "auth/station.html",
        form=form,
        station=station,
    )

@station_account.post("/account/station/lookup")
@login_required
def lookup_station_callsign():
    """Populate empty station fields using the user's callsign."""

    record = lookup_callsign(current_user.callsign)

    if record is None:
        flash(
            f"No callsign information was found for "
            f"{current_user.callsign}.",
            "warning",
        )
        return redirect(
            url_for("station_account.edit_station")
        )

    station = current_user.station

    if station is None:
        station = Station(
            user=current_user,
            station_name=f"{current_user.callsign} Station",
        )

    # Do not overwrite values the user entered manually.
    if not station.grid_square and record.grid_square:
        station.grid_square = record.grid_square.upper()

    if not station.dxcc_entity and record.dxcc_entity:
        station.dxcc_entity = record.dxcc_entity

    if not station.station_name or station.station_name == "Home Station":
        station.station_name = f"{record.callsign} Station"

    db.session.add(station)
    db.session.commit()

    flash(
        f"Station information was populated for "
        f"{record.callsign}.",
        "success",
    )

    return redirect(
        url_for("station_account.edit_station")
    )
