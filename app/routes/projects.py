from flask import render_template

from app.routes import main
from app.services.content import load_list


@main.get("/projects")
def projects():
    """Render current and planned amateur-radio projects."""

    return render_template(
        "projects.html",
        callsign="KG5FCZ",
        projects=load_list("projects.json"),
    )
