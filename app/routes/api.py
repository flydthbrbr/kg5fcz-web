from app.routes import main


@main.get("/health")
def health():
    """Return the application health status."""

    return {"status": "ok"}, 200
