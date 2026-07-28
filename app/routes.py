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


@main.get("/health")
def health():
    """Health endpoint used for deployment and monitoring checks."""

    return {"status": "ok"}, 200
