from bs4 import BeautifulSoup

from app.extensions import db
from app.models import ApiToken, User
from app.services.api_tokens import hash_token

from tests.test_auth import login, register


def create_second_user() -> User:
    user = User(
        email="second@example.com",
        callsign="W2XYZ",
    )
    user.set_password("correct-horse-battery-staple")

    db.session.add(user)
    db.session.commit()

    return user


def test_api_tokens_page_requires_login(client):
    response = client.get("/account/api-tokens")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_api_tokens_page_loads(client):
    register(client)
    login(client)

    response = client.get("/account/api-tokens")

    assert response.status_code == 200
    assert b"API tokens" in response.data
    assert b"Create token" in response.data


def test_user_can_create_api_token(app, client):
    register(client)
    login(client)

    response = client.post(
        "/account/api-tokens",
        data={
            "name": "Test Clock",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Copy this token now" in response.data
    assert b"Test Clock" in response.data

    with app.app_context():
        record = db.session.scalar(
            db.select(ApiToken)
        )

        assert record is not None
        assert record.name == "Test Clock"
        assert record.scope == "clock:read"
        assert record.revoked_at is None
        assert len(record.token_hash) == 64
        assert len(record.token_prefix) == 12


def test_raw_token_is_shown_only_once(app, client):
    register(client)
    login(client)

    response = client.post(
        "/account/api-tokens",
        data={
            "name": "One Time Token",
        },
        follow_redirects=True,
    )

    page = response.get_data(as_text=True)

    with app.app_context():
        record = db.session.scalar(
            db.select(ApiToken)
        )

        assert record is not None
        assert record.token_prefix in page

    assert "Copy this token now" in page

    response = client.get("/account/api-tokens")
    page = response.get_data(as_text=True)

    assert "Copy this token now" not in page
    assert "This is the only time" not in page


def test_database_stores_hash_not_raw_token(app, client):
    register(client)
    login(client)

    response = client.post(
        "/account/api-tokens",
        data={
            "name": "Hash Test",
        },
        follow_redirects=True,
    )

    page = response.get_data(as_text=True)

    soup = BeautifulSoup(page, "html.parser")

    token_field = soup.find(
        "textarea",
        id="new-api-token",
    )

    assert token_field is not None

    raw_token = token_field.get_text(strip=True)

    assert raw_token

    with app.app_context():
        record = db.session.scalar(
            db.select(ApiToken)
        )

        assert record is not None
        assert record.token_hash == hash_token(raw_token)
        assert record.token_hash != raw_token


def test_user_can_revoke_own_token(app, client):
    register(client)
    login(client)

    client.post(
        "/account/api-tokens",
        data={
            "name": "Revoke Me",
        },
    )

    with app.app_context():
        record = db.session.scalar(
            db.select(ApiToken)
        )

        assert record is not None
        token_id = record.id

    response = client.post(
        f"/account/api-tokens/{token_id}/revoke",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"was revoked" in response.data

    with app.app_context():
        record = db.session.get(ApiToken, token_id)

        assert record is not None
        assert record.revoked_at is not None


def test_user_cannot_revoke_another_users_token(app, client):
    register(client)

    with app.app_context():
        owner = create_second_user()

        record = ApiToken(
            user=owner,
            name="Other User Token",
            token_hash="a" * 64,
            token_prefix="otherprefix1",
            scope="clock:read",
        )

        db.session.add(record)
        db.session.commit()

        token_id = record.id

    login(client)

    response = client.post(
        f"/account/api-tokens/{token_id}/revoke",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"API token not found" in response.data

    with app.app_context():
        record = db.session.get(ApiToken, token_id)

        assert record is not None
        assert record.revoked_at is None


def test_revoke_route_rejects_get(client):
    response = client.get(
        "/account/api-tokens/1/revoke"
    )

    assert response.status_code == 405


def test_created_token_list_shows_prefix_not_hash(app, client):
    register(client)
    login(client)

    client.post(
        "/account/api-tokens",
        data={
            "name": "Listed Token",
        },
    )

    with app.app_context():
        record = db.session.scalar(
            db.select(ApiToken)
        )

        assert record is not None
        prefix = record.token_prefix
        token_hash = record.token_hash

    response = client.get("/account/api-tokens")
    page = response.get_data(as_text=True)

    assert prefix in page
    assert token_hash not in page
