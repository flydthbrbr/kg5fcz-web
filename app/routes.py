from flask import Blueprint, render_template

from app.services.content import load_list


main = Blueprint("main", __name__)


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


@main.get("/station")
def station():
    """Render station equipment and operating information."""

    return render_template(
        "station.html",
        callsign="KG5FCZ",
        equipment=load_list("equipment.json"),
    )


@main.get("/projects")
def projects():
    """Render current and planned amateur-radio projects."""

    return render_template(
        "projects.html",
        callsign="KG5FCZ",
        projects=load_list("projects.json"),
    )


@main.get("/health")
def health():
    """Health endpoint used for deployment checks."""

    return {"status": "ok"}, 200
