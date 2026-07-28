import json
from pathlib import Path
from typing import Any


DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"


class ContentLoadError(RuntimeError):
    """Raised when structured website content cannot be loaded."""


def load_json_file(filename: str) -> Any:
    """Load JSON from the application's data directory."""

    if Path(filename).name != filename:
        raise ContentLoadError(f"Invalid content filename: {filename}")

    file_path = DATA_DIRECTORY / filename

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as exc:
        raise ContentLoadError(
            f"Content file does not exist: {filename}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ContentLoadError(
            f"Invalid JSON in {filename}, "
            f"line {exc.lineno}, column {exc.colno}"
        ) from exc
    except OSError as exc:
        raise ContentLoadError(
            f"Unable to read content file: {filename}"
        ) from exc


def load_list(filename: str) -> list[dict[str, Any]]:
    """Load a JSON file and require a list of objects."""

    content = load_json_file(filename)

    if not isinstance(content, list):
        raise ContentLoadError(
            f"Content file must contain a JSON list: {filename}"
        )

    if not all(isinstance(item, dict) for item in content):
        raise ContentLoadError(
            f"Every item must be a JSON object: {filename}"
        )

    return content
