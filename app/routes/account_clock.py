from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import ClockSettingsForm
from app.services.clock_settings import (
    get_or_create_clock_settings,
)


account_clock = Blueprint(
    "account_clock",
    __name__,
)


@account_clock.route(
    "/account/clock",
    methods=["GET", "POST"],
)
@login_required
def edit_clock_settings():
    """Create or update the current user's clock settings."""

    settings = get_or_create_clock_settings(current_user)
    form = ClockSettingsForm(obj=settings)

    if form.validate_on_submit():
        settings.theme = form.theme.data
        settings.units = form.units.data
        settings.map_projection = form.map_projection.data
        settings.show_satellites = form.show_satellites.data
        settings.show_dx_cluster = form.show_dx_cluster.data
        settings.show_weather = form.show_weather.data
        settings.show_moon = form.show_moon.data
        settings.show_grayline = form.show_grayline.data
        settings.default_zoom = form.default_zoom.data

        db.session.add(settings)
        db.session.commit()

        flash(
            "Your clock settings have been updated.",
            "success",
        )

        return redirect(
            url_for("account_clock.edit_clock_settings")
        )

    return render_template(
        "auth/clock_settings.html",
        form=form,
        settings=settings,
    )
