from app.extensions import db
from app.models import User


EMAIL = "operator@example.com"
CALLSIGN = "W1ABC"
PASSWORD = "correct-horse-battery-staple"


def register(client):
    return client.post(
        "/register",
        data={
            "email": EMAIL,
            "callsign": CALLSIGN,
            "password": PASSWORD,
            "password_confirm": PASSWORD,
        },
        follow_redirects=True,
    )


def login(client, identity=EMAIL, password=PASSWORD):
    return client.post(
        "/login",
        data={
            "identity": identity,
            "password": password,
        },
        follow_redirects=True,
    )


def test_registration_creates_user(app, client):
    response = register(client)

    assert response.status_code == 200
    assert b"Sign in" in response.data

    with app.app_context():
        user = db.session.scalar(
            db.select(User).where(User.email == EMAIL)
        )

        assert user is not None
        assert user.callsign == CALLSIGN
        assert user.password_hash != PASSWORD
        assert user.check_password(PASSWORD)


def test_duplicate_email_is_rejected(client):
    register(client)

    response = client.post(
        "/register",
        data={
            "email": EMAIL.upper(),
            "callsign": "W2XYZ",
            "password": PASSWORD,
            "password_confirm": PASSWORD,
        },
        follow_redirects=True,
    )

    assert b"already uses that email address" in response.data


def test_duplicate_callsign_is_rejected(client):
    register(client)

    response = client.post(
        "/register",
        data={
            "email": "other@example.com",
            "callsign": CALLSIGN.lower(),
            "password": PASSWORD,
            "password_confirm": PASSWORD,
        },
        follow_redirects=True,
    )

    assert b"already uses that callsign" in response.data


def test_login_with_email(client):
    register(client)

    response = login(client)

    assert response.status_code == 200
    assert b"My Account" in response.data
    assert CALLSIGN.encode() in response.data
    assert EMAIL.encode() in response.data

def test_login_with_callsign(client):
    register(client)

    response = login(client, identity=CALLSIGN.lower())

    assert response.status_code == 200
    assert b"My Account" in response.data
    assert CALLSIGN.encode() in response.data


def test_invalid_password_is_rejected(client):
    register(client)

    response = login(client, password="wrong-password-value")

    assert b"Invalid email, callsign, or password" in response.data


def test_account_requires_login(client):
    response = client.get("/account")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_auth_check_for_guest(client):
    response = client.get("/auth/check")

    assert response.status_code == 401
    assert response.get_json() == {"authenticated": False}


def test_auth_check_for_logged_in_user(client):
    register(client)
    login(client)

    response = client.get("/auth/check")

    assert response.status_code == 200
    assert response.get_json()["authenticated"] is True
    assert response.get_json()["user"]["callsign"] == CALLSIGN


def test_logout_ends_session(client):
    register(client)
    login(client)

    response = client.post("/logout", follow_redirects=True)

    assert response.status_code == 200

    auth_response = client.get("/auth/check")
    assert auth_response.status_code == 401


def test_logout_rejects_get(client):
    response = client.get("/logout")

    assert response.status_code == 405
