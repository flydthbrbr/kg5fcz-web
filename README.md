# KG5FCZ Website

The Flask application for https://kg5fcz.com.

## Architecture

- Caddy handles HTTPS and reverse proxying.
- Gunicorn runs the Flask application.
- systemd manages Gunicorn.
- OpenHamClock remains available at https://clock.kg5fcz.com.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
flask --app wsgi run --debug
