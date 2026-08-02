import re

from app.extensions import db
from app.models import ClockSettings

from tests.test_auth import login, register


def test_clock_settings_requires_login(client):
    response = client.get("/account/clock")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_clock_settings_page_loads(client):
    register(client)
    login(client)

    response = client.get("/account/clock")

    assert response.status_code == 200
    assert b"Clock settings" in response.data
    assert b"Theme" in response.data
    assert b"Map projection" in response.data
    assert b"Show satellites" in response.data


def test_get_creates_uncommitted_default_settings(app, client):
    register(client)
    login(client)

    response = client.get("/account/clock")

    assert response.status_code == 200

    with app.app_context():
        settings = db.session.scalar(
            db.select(ClockSettings)
        )

        # The service adds defaults to the session, but a GET request
        # should not permanently save them.
        assert settings is None


def test_saved_settings_are_displayed(client):
    register(client)
    login(client)

    client.post(
        "/account/clock",
        data={
            "theme": "light",
            "units": "metric",
            "map_projection": "azimuthal",
            "show_satellites": "y",
            "show_dx_cluster": "y",
            "show_weather": "y",
            "show_moon": "y",
            "show_grayline": "y",
            "default_zoom": "5",
        },
    )

    response = client.get("/account/clock")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'value="light"' in page
    assert 'value="metric"' in page
    assert 'value="azimuthal"' in page
    assert 'name="default_zoom"' in page
    assert 'value="5"' in page
    assert 'selected' in page

def test_clock_settings_update_existing_row(app, client):
    register(client)
    login(client)

    initial = {
        "theme": "dark",
        "units": "imperial",
        "map_projection": "mercator",
        "show_satellites": "y",
        "show_dx_cluster": "y",
        "show_weather": "y",
        "show_moon": "y",
        "show_grayline": "y",
        "default_zoom": "2",
    }

    updated = {
        "theme": "light",
        "units": "metric",
        "map_projection": "azimuthal",
        "default_zoom": "6",
    }

    client.post("/account/clock", data=initial)
    client.post("/account/clock", data=updated)

    with app.app_context():
        rows = db.session.scalars(
            db.select(ClockSettings)
        ).all()

        assert len(rows) == 1
        assert rows[0].theme == "light"
        assert rows[0].units == "metric"
        assert rows[0].default_zoom == 6


def test_invalid_zoom_is_rejected(app, client):
    register(client)
    login(client)

    response = client.post(
        "/account/clock",
        data={
            "theme": "dark",
            "units": "imperial",
            "map_projection": "mercator",
            "default_zoom": "99",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Zoom must be between 1 and 10" in response.data

    with app.app_context():
        settings = db.session.scalar(
            db.select(ClockSettings)
        )

        assert settings is None
