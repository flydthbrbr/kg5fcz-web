from app.extensions import db
from app.models import ClockSettings, Station, User, UserProfile

from tests.test_auth import login, register


def test_clock_api_requires_authentication(client):
    response = client.get("/api/v1/account/clock")

    assert response.status_code == 401
    assert response.get_json() == {
        "authenticated": False,
        "error": "Authentication required.",
    }


def test_clock_api_returns_default_configuration(client):
    register(client)
    login(client)

    response = client.get("/api/v1/account/clock")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["schema_version"] == 1
    assert payload["authenticated"] is True
    assert payload["generated_at"]

    assert payload["operator"]["callsign"] == "W1ABC"
    assert payload["operator"]["display_name"] is None
    assert payload["operator"]["timezone"] == "UTC"

    assert payload["station"]["configured"] is False
    assert payload["station"]["station_name"] is None
    assert payload["station"]["grid_square"] is None

    assert payload["clock"] == {
        "theme": "dark",
        "units": "imperial",
        "map_projection": "mercator",
        "show_satellites": True,
        "show_dx_cluster": True,
        "show_weather": True,
        "show_moon": True,
        "show_grayline": True,
        "default_zoom": 2,
    }


def test_clock_api_get_does_not_save_default_settings(
    app,
    client,
):
    register(client)
    login(client)

    response = client.get("/api/v1/account/clock")

    assert response.status_code == 200

    with app.app_context():
        settings = db.session.scalar(
            db.select(ClockSettings)
        )

        assert settings is None


def test_clock_api_returns_saved_clock_settings(
    app,
    client,
):
    register(client)
    login(client)

    client.post(
        "/account/clock",
        data={
            "theme": "light",
            "units": "metric",
            "map_projection": "azimuthal",
            "show_satellites": "y",
            "show_weather": "y",
            "show_grayline": "y",
            "default_zoom": "5",
        },
    )

    response = client.get("/api/v1/account/clock")
    payload = response.get_json()

    assert response.status_code == 200

    assert payload["clock"] == {
        "theme": "light",
        "units": "metric",
        "map_projection": "azimuthal",
        "show_satellites": True,
        "show_dx_cluster": False,
        "show_weather": True,
        "show_moon": False,
        "show_grayline": True,
        "default_zoom": 5,
    }

    with app.app_context():
        rows = db.session.scalars(
            db.select(ClockSettings)
        ).all()

        assert len(rows) == 1


def test_clock_api_returns_profile_data(app, client):
    register(client)

    with app.app_context():
        user = db.session.scalar(
            db.select(User).where(User.callsign == "W1ABC")
        )

        assert user is not None

        profile = UserProfile(
            user=user,
            display_name="Test Operator",
            grid_square="EM20",
            timezone="America/Chicago",
            preferred_units="imperial",
        )

        db.session.add(profile)
        db.session.commit()

    login(client)

    response = client.get("/api/v1/account/clock")
    payload = response.get_json()
    operator = payload["operator"]
    station = payload["station"]

    assert response.status_code == 200
    assert operator["callsign"] == "W1ABC"
    assert operator["display_name"] == "Test Operator"
    assert operator["timezone"] == "America/Chicago"
    assert station["grid_square"] == "EM20"

def test_clock_api_returns_station_data(app, client):
    register(client)

    with app.app_context():
        user = db.session.scalar(
            db.select(User).where(User.callsign == "W1ABC")
        )

        assert user is not None

        station = Station(
            user=user,
            station_name="Test Station",
            grid_square="FN31",
            primary_rig="Test Rig",
            primary_antenna="Dipole",
            license_class="General",
            dxcc_entity="United States",
        )

        db.session.add(station)
        db.session.commit()

    login(client)

    response = client.get("/api/v1/account/clock")
    station_payload = response.get_json()["station"]

    assert response.status_code == 200
    assert station_payload == {
        "configured": True,
        "station_name": "Test Station",
        "grid_square": "FN31",
        "dxcc_entity": "United States",
        "primary_rig": "Test Rig",
        "primary_antenna": "Dipole",
    }

def test_station_grid_overrides_profile_grid(app, client):
    register(client)

    with app.app_context():
        user = db.session.scalar(
            db.select(User).where(User.callsign == "W1ABC")
        )

        assert user is not None

        profile = UserProfile(
            user=user,
            display_name="Test Operator",
            grid_square="EM20",
            timezone="America/Chicago",
            preferred_units="imperial",
        )

        station = Station(
            user=user,
            station_name="Portable Station",
            grid_square="FN31",
        )

        db.session.add_all([profile, station])
        db.session.commit()

    login(client)

    response = client.get("/api/v1/account/clock")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["station"]["grid_square"] == "FN31"

def test_clock_api_is_get_only(client):
    response = client.post("/api/v1/account/clock")

    assert response.status_code == 405
