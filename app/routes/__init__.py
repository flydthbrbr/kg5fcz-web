from flask import Blueprint


main = Blueprint("main", __name__)


# Import route modules after creating the blueprint.
# These imports register each route on `main`.
from app.routes import api, projects, public, station  # noqa: E402, F401
