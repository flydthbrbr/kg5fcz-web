from flask import Flask

from app.extensions import csrf, db, login_manager, migrate


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the KG5FCZ Flask application."""

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="development-only-change-later",
        SQLALCHEMY_DATABASE_URI=(
            f"sqlite:///{app.instance_path}/kg5fcz.sqlite"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CALLSIGN_PROVIDER="hamdb",
        HAMDB_BASE_URL="http://api.hamdb.org",
        HAMDB_APPLICATION_NAME="kg5fcz-web",
        CALLSIGN_LOOKUP_TIMEOUT_SECONDS=5.0,
        CALLSIGN_PROVIDER_FALLBACK_ENABLED=True,
    )

    app.config.from_pyfile("config.py", silent=True)

    # Test settings must be applied before db.init_app().
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to access that page."
    login_manager.login_message_category = "info"

    from app.models import Station, User, UserProfile

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return db.session.get(User, int(user_id))
        except (TypeError, ValueError):
            return None

    from app.routes import main
    from app.routes.auth import auth
    from app.routes.account_station import station_account

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(station_account)

    return app
