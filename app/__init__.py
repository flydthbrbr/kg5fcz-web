from flask import Flask


def create_app() -> Flask:
    """Create and configure the KG5FCZ Flask application."""

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="development-only-change-later",
    )

    app.config.from_pyfile("config.py", silent=True)

    from app.routes import main

    app.register_blueprint(main)

    return app
