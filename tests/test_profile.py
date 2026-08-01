from app.extensions import db
from app.models import UserProfile

from tests.test_auth import login, register


def test_profile_requires_login(client):
    response = client.get("/account/profile")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_user_can_create_profile(app, client):
    register(client)
    login(client)

    response = client.post(
        "/account/profile",
        data={
            "display_name": "Brian",
            "grid_square": "EM20",
            "timezone": "America/Chicago",
            "preferred_units": "imperial",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Your profile has been updated" in response.data

    with app.app_context():
        profile = db.session.scalar(db.select(UserProfile))

        assert profile is not None
        assert profile.display_name == "Brian"
        assert profile.grid_square == "EM20"


def test_grid_square_is_normalized(app, client):
    register(client)
    login(client)

    client.post(
        "/account/profile",
        data={
            "display_name": "",
            "grid_square": "em20ab",
            "timezone": "UTC",
            "preferred_units": "metric",
        },
    )

    with app.app_context():
        profile = db.session.scalar(db.select(UserProfile))

        assert profile.grid_square == "EM20AB"


def test_invalid_grid_square_is_rejected(client):
    register(client)
    login(client)

    response = client.post(
        "/account/profile",
        data={
            "display_name": "Brian",
            "grid_square": "INVALID",
            "timezone": "UTC",
            "preferred_units": "imperial",
        },
        follow_redirects=True,
    )

    assert b"Enter a valid" in response.data
