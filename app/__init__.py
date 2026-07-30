from flask import Flask

from app.extensions import db, migrate, login_manager

def create_app() -> Flask:
    """Create and configure the KG5FCZ Flask application."""

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="development-only-change-later",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{app.instance_path}/kg5fcz.sqlite",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    app.config.from_pyfile("config.py", silent=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import user

    from app.routes import main

    app.register_blueprint(main)

    return app
