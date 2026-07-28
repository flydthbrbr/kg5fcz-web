from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.get("/")
def index():
    """Render the public home page."""

    awards = [
        {
            "number": "107882",
            "name": "World Radio Friendship Award",
            "date": "July 18, 2026",
            "endorsement": "20M Mixed",
        },
        {
            "number": "57704",
            "name": "United States Counties Award",
            "date": "July 18, 2026",
            "endorsement": "100 Counties Mixed",
        },
        {
            "number": "92294",
            "name": "Grid Squared Award",
            "date": "July 18, 2026",
            "endorsement": "QRZ Award",
        },
    ]

    projects = [
        {
            "name": "OpenHamClock",
            "description": (
                "A browser-based amateur-radio information display hosted "
                "at clock.kg5fcz.com."
            ),
            "url": "https://clock.kg5fcz.com/",
            "status": "Live",
        },
        {
            "name": "Station Overview",
            "description": (
                "Radios, antennas, accessories, and operating setup."
            ),
            "url": None,
            "status": "Coming soon",
        },
        {
            "name": "Build Notes",
            "description": (
                "Technical notes, software modifications, and experiments."
            ),
            "url": None,
            "status": "Coming soon",
        },
    ]

    return render_template(
        "index.html",
        callsign="KG5FCZ",
        awards=awards,
        projects=projects,
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

    equipment = [
        {
            "category": "Primary radio",
            "name": "Yaesu FTX-1 Optima",
            "description": (
                "Portable and base-station operation with CAT control, "
                "digital-mode support, and software integration."
            ),
        },
        {
            "category": "Station software",
            "name": "OpenHamClock",
            "description": (
                "A browser-based amateur-radio dashboard hosted at "
                "clock.kg5fcz.com."
            ),
        },
        {
            "category": "Operating",
            "name": "Digital and mixed-mode operation",
            "description": (
                "Experimentation with digital modes, logging, rig control, "
                "and amateur-radio software."
            ),
        },
    ]

    return render_template(
        "station.html",
        callsign="KG5FCZ",
        equipment=equipment,
    )


@main.get("/projects")
def projects():
    """Render current and planned amateur-radio projects."""

    project_list = [
        {
            "name": "OpenHamClock",
            "status": "Active",
            "description": (
                "A web-based amateur-radio information display with plans "
                "for profiles, logging, ADIF tools, and station integration."
            ),
            "url": "https://clock.kg5fcz.com/",
        },
        {
            "name": "KG5FCZ Website",
            "status": "Active",
            "description": (
                "This Flask website, including station information, project "
                "documentation, QRZ integration, and future logbook tools."
            ),
            "url": None,
        },
        {
            "name": "FLRIG FTX-1 Support",
            "status": "Research",
            "description": (
                "Investigation and development work related to improving "
                "Yaesu FTX-1 Optima support in FLRIG."
            ),
            "url": None,
        },
    ]

    return render_template(
        "projects.html",
        callsign="KG5FCZ",
        projects=project_list,
    )


@main.get("/health")
def health():
    """Health endpoint used for deployment and monitoring checks."""

    return {"status": "ok"}, 200
