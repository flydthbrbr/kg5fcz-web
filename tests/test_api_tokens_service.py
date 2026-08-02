from app.extensions import db
from app.models import ApiToken, User
from app.services.api_tokens import (
    generate_api_token,
    hash_token,
    revoke_api_token,
    verify_api_token,
)


def create_user() -> User:
    user = User(
        email="token@example.com",
        callsign="W1TOK",
    )
    user.set_password("correct-horse-battery-staple")

    db.session.add(user)
    db.session.commit()

    return user


def test_generate_token_returns_raw_token_and_hashes_storage(app):
    with app.app_context():
        user = create_user()

        record, raw_token = generate_api_token(user)
        db.session.commit()

        assert raw_token
        assert record.id is not None
        assert record.token_hash == hash_token(raw_token)
        assert record.token_hash != raw_token
        assert record.token_prefix == raw_token[:12]
        assert record.scope == "clock:read"


def test_generated_tokens_are_unique(app):
    with app.app_context():
        user = create_user()

        first_record, first_raw = generate_api_token(user)
        second_record, second_raw = generate_api_token(user)

        db.session.commit()

        assert first_raw != second_raw
        assert first_record.token_hash != second_record.token_hash


def test_verify_token_returns_active_record(app):
    with app.app_context():
        user = create_user()

        record, raw_token = generate_api_token(user)
        db.session.commit()

        verified = verify_api_token(
            raw_token,
            required_scope="clock:read",
        )

        assert verified is not None
        assert verified.id == record.id
        assert verified.user_id == user.id
        assert verified.last_used_at is not None


def test_verify_token_rejects_invalid_token(app):
    with app.app_context():
        create_user()

        assert verify_api_token("not-a-real-token") is None


def test_verify_token_rejects_wrong_scope(app):
    with app.app_context():
        user = create_user()

        _, raw_token = generate_api_token(
            user,
            scope="clock:read",
        )
        db.session.commit()

        verified = verify_api_token(
            raw_token,
            required_scope="clock:write",
        )

        assert verified is None


def test_revoked_token_is_rejected(app):
    with app.app_context():
        user = create_user()

        record, raw_token = generate_api_token(user)
        db.session.commit()

        revoke_api_token(record)
        db.session.commit()

        assert record.revoked_at is not None
        assert verify_api_token(raw_token) is None


def test_generate_token_does_not_commit_implicitly(app):
    with app.app_context():
        user = create_user()

        record, _ = generate_api_token(user)

        assert record in db.session.new

        db.session.rollback()

        saved = db.session.scalar(
            db.select(ApiToken).where(
                ApiToken.user_id == user.id
            )
        )

        assert saved is None


def test_revoke_does_not_commit_implicitly(app):
    with app.app_context():
        user = create_user()

        record, _ = generate_api_token(user)
        db.session.commit()

        revoke_api_token(record)

        assert record.revoked_at is not None
        assert record in db.session.dirty

        db.session.rollback()
        db.session.refresh(record)

        assert record.revoked_at is None
