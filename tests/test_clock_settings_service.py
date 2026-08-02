from app.extensions import db
from app.models import ClockSettings, User
from app.services.clock_settings import (
    get_or_create_clock_settings,
)


def create_user() -> User:
    user = User(
        email="clock@example.com",
        callsign="W1CLK",
    )
    user.set_password("correct-horse-battery-staple")

    db.session.add(user)
    db.session.commit()

    return user


def test_service_creates_default_clock_settings(app):
    with app.app_context():
        user = create_user()

        settings = get_or_create_clock_settings(user)

        db.session.commit()

        assert settings.id is not None
        assert settings.user_id == user.id
        assert settings.theme == "dark"
        assert settings.units == "imperial"
        assert settings.map_projection == "mercator"
        assert settings.show_satellites is True
        assert settings.show_dx_cluster is True
        assert settings.show_weather is True
        assert settings.show_moon is True
        assert settings.show_grayline is True
        assert settings.default_zoom == 2


def test_service_returns_existing_settings(app):
    with app.app_context():
        user = create_user()

        existing = ClockSettings(
            user=user,
            theme="light",
            units="metric",
            map_projection="azimuthal",
            show_satellites=False,
            show_dx_cluster=False,
            show_weather=False,
            show_moon=False,
            show_grayline=False,
            default_zoom=4,
        )

        db.session.add(existing)
        db.session.commit()

        returned = get_or_create_clock_settings(user)

        assert returned.id == existing.id
        assert returned.theme == "light"
        assert returned.units == "metric"
        assert returned.default_zoom == 4


def test_service_creates_only_one_row(app):
    with app.app_context():
        user = create_user()

        first = get_or_create_clock_settings(user)
        db.session.commit()

        second = get_or_create_clock_settings(user)
        db.session.commit()

        settings_rows = db.session.scalars(
            db.select(ClockSettings).where(
                ClockSettings.user_id == user.id
            )
        ).all()

        assert first.id == second.id
        assert len(settings_rows) == 1


def test_service_does_not_commit_implicitly(app):
    with app.app_context():
        user = create_user()

        settings = get_or_create_clock_settings(user)

        assert settings in db.session.new

        db.session.rollback()

        saved = db.session.scalar(
            db.select(ClockSettings).where(
                ClockSettings.user_id == user.id
            )
        )

        assert saved is None
