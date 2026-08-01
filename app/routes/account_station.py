from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import StationForm
from app.models import Station
from app.services.callsign import lookup_callsign
from app.services.callsign_cache import lookup_callsign_cached
from app.services.callsign import CallsignRecord
from app.services.station_review import build_station_review

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
@station_account.post("/account/station/lookup/preview")
@login_required
def preview_station_lookup():
    """Look up callsign data and store it for review."""

    record = lookup_callsign_cached(current_user.callsign)

    if record is None:
        session.pop("station_lookup_preview", None)

        flash(
            f"No callsign information was found for "
            f"{current_user.callsign}.",
            "warning",
        )

        return redirect(
            url_for("station_account.edit_station")
        )

    session["station_lookup_preview"] = {
        "callsign": record.callsign,
        "display_name": record.display_name,
        "grid_square": record.grid_square,
        "dxcc_entity": record.dxcc_entity,
        "cq_zone": record.cq_zone,
        "itu_zone": record.itu_zone,
        "provider": record.provider,
        "from_cache": record.from_cache,
        "stale": record.stale,
        "looked_up_at": (
            record.looked_up_at.isoformat()
            if record.looked_up_at
            else None
        ),
    }

    return redirect(
        url_for("station_account.review_station_lookup")
    )

@station_account.get("/account/station/lookup/review")
@login_required
def review_station_lookup():
    """Show callsign data before applying it to the station."""

    preview = session.get("station_lookup_preview")

    if preview is None:
        flash(
            "There is no callsign lookup result to review.",
            "warning",
        )
        return redirect(
            url_for("station_account.edit_station")
        )

    record = CallsignRecord(
        callsign=preview["callsign"],
        display_name=preview.get("display_name"),
        grid_square=preview.get("grid_square"),
        dxcc_entity=preview.get("dxcc_entity"),
        cq_zone=preview.get("cq_zone"),
        itu_zone=preview.get("itu_zone"),
        provider=preview.get("provider"),
        from_cache=preview.get("from_cache", False),
        stale=preview.get("stale", False),
    )

    review_items = build_station_review(
        current_user.station,
        record,
    )

    return render_template(
        "auth/station_lookup_review.html",
        preview=preview,
        station=current_user.station,
        review_items=review_items,
    )


@station_account.post("/account/station/lookup/apply")
@login_required
def apply_station_lookup():
    """Apply selected callsign lookup values to the station."""

    preview = session.get("station_lookup_preview")

    if preview is None:
        flash(
            "There is no callsign lookup result to apply.",
            "warning",
        )
        return redirect(
            url_for("station_account.edit_station")
        )

    selected_fields = set(
        request.form.getlist("fields")
    )

    allowed_fields = {
        "station_name",
        "grid_square",
        "dxcc_entity",
    }

    selected_fields &= allowed_fields

    station = current_user.station

    if station is None:
        station = Station(
            user=current_user,
            station_name="Home Station",
        )

    if "station_name" in selected_fields:
        station.station_name = (
            f"{preview['callsign']} Station"
        )

    if (
        "grid_square" in selected_fields
        and preview.get("grid_square")
    ):
        station.grid_square = (
            preview["grid_square"].strip().upper()
        )

    if (
        "dxcc_entity" in selected_fields
        and preview.get("dxcc_entity")
    ):
        station.dxcc_entity = (
            preview["dxcc_entity"].strip()
        )

    db.session.add(station)
    db.session.commit()

    session.pop("station_lookup_preview", None)

    flash(
        "Selected callsign values were applied.",
        "success",
    )

    return redirect(
        url_for("station_account.edit_station")
    )
