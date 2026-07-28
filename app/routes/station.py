from flask import render_template

from app.routes import main
from app.services.content import load_list


@main.get("/station")
def station():
    """Render station equipment and operating information."""

    return render_template(
        "station.html",
        callsign="KG5FCZ",
        equipment=load_list("equipment.json"),
    )
