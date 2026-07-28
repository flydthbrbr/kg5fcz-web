from app import create_app


def test_home_page():
    app = create_app()
    app.config.update(TESTING=True)

    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"KG5FCZ" in response.data


def test_health_endpoint():
    app = create_app()
    app.config.update(TESTING=True)

    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

def test_about_page():
    app = create_app()
    app.config.update(TESTING=True)

    client = app.test_client()
    response = client.get("/about")

    assert response.status_code == 200
    assert b"Radio, software, and experimentation" in response.data


def test_station_page():
    app = create_app()
    app.config.update(TESTING=True)

    client = app.test_client()
    response = client.get("/station")

    assert response.status_code == 200
    assert b"Yaesu FTX-1 Optima" in response.data


def test_projects_page():
    app = create_app()
    app.config.update(TESTING=True)

    client = app.test_client()
    response = client.get("/projects")

    assert response.status_code == 200
    assert b"OpenHamClock" in response.data
