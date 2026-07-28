from flask import render_template

from app.routes import main
from app.services.content import load_list


@main.get("/")
def index():
    """Render the public home page."""

    return render_template(
        "index.html",
        callsign="KG5FCZ",
        awards=load_list("awards.json"),
        projects=load_list("projects.json"),
    )


@main.get("/about")
def about():
    """Render information about KG5FCZ and the station."""

    return render_template(
        "about.html",
        callsign="KG5FCZ",
    )
