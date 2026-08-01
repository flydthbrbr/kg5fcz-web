from app.extensions import db
from app.models import Station
from tests.test_auth import login, register


def test_station_profile_requires_login(client):
    response = client.get("/account/station")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_station_profile_page_loads(client):
    register(client)
    login(client)

    response = client.get("/account/station")

    assert response.status_code == 200
    assert b"Station profile" in response.data
    assert b"Station name" in response.data
    assert b"Primary rig" in response.data


def test_user_can_create_station(app, client):
    register(client)
    login(client)

    response = client.post(
        "/account/station",
        data={
            "station_name": "KG5FCZ Home",
            "grid_square": "EM20",
            "primary_rig": "Yaesu FTX-1 Optima",
            "primary_antenna": "Dipole",
            "license_class": "Amateur Extra",
            "dxcc_entity": "United States",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"station information has been updated" in response.data

    with app.app_context():
        station = db.session.scalar(db.select(Station))

        assert station is not None
        assert station.station_name == "KG5FCZ Home"
        assert station.grid_square == "EM20"
        assert station.primary_rig == "Yaesu FTX-1 Optima"
        assert station.primary_antenna == "Dipole"
        assert station.license_class == "Amateur Extra"
        assert station.dxcc_entity == "United States"


def test_station_values_are_displayed_after_save(client):
    register(client)
    login(client)

    client.post(
        "/account/station",
        data={
            "station_name": "Portable Station",
            "grid_square": "EM20AB",
            "primary_rig": "Yaesu FTX-1 Optima",
            "primary_antenna": "Portable vertical",
            "license_class": "Amateur Extra",
            "dxcc_entity": "United States",
        },
    )

    response = client.get("/account/station")

    assert response.status_code == 200
    assert b'Portable Station' in response.data
    assert b'EM20AB' in response.data
    assert b'Yaesu FTX-1 Optima' in response.data
    assert b'Portable vertical' in response.data


def test_station_update_does_not_create_duplicate(app, client):
    register(client)
    login(client)

    original = {
        "station_name": "Original Station",
        "grid_square": "EM20",
        "primary_rig": "First Radio",
        "primary_antenna": "Dipole",
        "license_class": "General",
        "dxcc_entity": "United States",
    }

    updated = {
        "station_name": "Updated Station",
        "grid_square": "EM20AB",
        "primary_rig": "Yaesu FTX-1 Optima",
        "primary_antenna": "Vertical",
        "license_class": "Amateur Extra",
        "dxcc_entity": "United States",
    }

    client.post("/account/station", data=original)
    client.post("/account/station", data=updated)

    with app.app_context():
        stations = db.session.scalars(db.select(Station)).all()

        assert len(stations) == 1
        assert stations[0].station_name == "Updated Station"
        assert stations[0].grid_square == "EM20AB"
        assert stations[0].primary_rig == "Yaesu FTX-1 Optima"


def test_grid_square_is_normalized(app, client):
    register(client)
    login(client)

    client.post(
        "/account/station",
        data={
            "station_name": "Home Station",
            "grid_square": "em20ab",
            "primary_rig": "",
            "primary_antenna": "",
            "license_class": "",
            "dxcc_entity": "",
        },
    )

    with app.app_context():
        station = db.session.scalar(db.select(Station))

        assert station is not None
        assert station.grid_square == "EM20AB"


def test_invalid_grid_square_is_rejected(app, client):
    register(client)
    login(client)

    response = client.post(
        "/account/station",
        data={
            "station_name": "Home Station",
            "grid_square": "INVALID",
            "primary_rig": "",
            "primary_antenna": "",
            "license_class": "",
            "dxcc_entity": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Enter a valid" in response.data

    with app.app_context():
        station = db.session.scalar(db.select(Station))
        assert station is None
def test_callsign_lookup_requires_login(client):
    response = client.post("/account/station/lookup")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_callsign_lookup_creates_station(app, client):
    register(client)
    login(client)

    response = client.post(
        "/account/station/lookup",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Station information was populated" in response.data

    with app.app_context():
        station = db.session.scalar(db.select(Station))

        assert station is not None
        assert station.station_name == "W1ABC Station"
        assert station.grid_square == "FN31"
        assert station.dxcc_entity == "United States"


def test_callsign_lookup_does_not_overwrite_manual_values(
    app,
    client,
):
    register(client)
    login(client)

    client.post(
        "/account/station",
        data={
            "station_name": "Portable Station",
            "grid_square": "EM20AB",
            "primary_rig": "Yaesu FTX-1 Optima",
            "primary_antenna": "Portable vertical",
            "license_class": "Amateur Extra",
            "dxcc_entity": "Custom Entity",
        },
    )

    client.post("/account/station/lookup")

    with app.app_context():
        station = db.session.scalar(db.select(Station))

        assert station.station_name == "Portable Station"
        assert station.grid_square == "EM20AB"
        assert station.dxcc_entity == "Custom Entity"
        assert station.primary_rig == "Yaesu FTX-1 Optima"


def test_lookup_route_rejects_get(client):
    response = client.get("/account/station/lookup")

    assert response.status_code == 405
