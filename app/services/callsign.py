from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import current_app


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CallsignRecord:
    """Normalized amateur-radio callsign information."""

    callsign: str
    display_name: str | None = None
    grid_square: str | None = None
    dxcc_entity: str | None = None
    cq_zone: int | None = None
    itu_zone: int | None = None


class CallsignProviderError(RuntimeError):
    """Raised when a callsign provider cannot complete a lookup."""


class CallsignProvider(Protocol):
    """Interface implemented by callsign-data providers."""

    def lookup(self, callsign: str) -> CallsignRecord | None:
        """Return a normalized record or None when not found."""


def normalize_callsign(callsign: str) -> str:
    """Normalize a callsign before passing it to a provider."""

    return callsign.strip().upper()


def optional_text(value: object) -> str | None:
    """Return stripped text or None."""

    if value is None:
        return None

    text = str(value).strip()
    return text or None


def optional_integer(value: object) -> int | None:
    """Convert a provider value to an integer when possible."""

    text = optional_text(value)

    if text is None:
        return None

    try:
        return int(text)
    except (TypeError, ValueError):
        return None


def build_display_name(callsign_data: dict[str, object]) -> str | None:
    """Build a display name from provider name fields."""

    first_name = optional_text(
        callsign_data.get("fname")
        or callsign_data.get("first_name")
    )

    middle_name = optional_text(
        callsign_data.get("mi")
        or callsign_data.get("middle_name")
    )

    last_name = optional_text(
        callsign_data.get("name")
        or callsign_data.get("last_name")
    )

    parts = [
        value
        for value in (first_name, middle_name, last_name)
        if value
    ]

    return " ".join(parts) or None


class HamDBCallsignProvider:
    """Retrieve normalized callsign data from HamDB."""

    def __init__(
        self,
        *,
        base_url: str,
        application_name: str,
        timeout_seconds: float,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.application_name = application_name
        self.timeout_seconds = timeout_seconds

    def lookup(self, callsign: str) -> CallsignRecord | None:
        normalized = normalize_callsign(callsign)

        if not normalized:
            return None

        encoded_callsign = quote(normalized, safe="")
        encoded_app_name = quote(self.application_name, safe="")

        url = (
            f"{self.base_url}/"
            f"{encoded_callsign}/json/{encoded_app_name}"
        )

        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": (
                    f"{self.application_name}/1.0 "
                    "(callsign lookup)"
                ),
            },
            method="GET",
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                payload = json.load(response)

        except HTTPError as exc:
            raise CallsignProviderError(
                f"HamDB returned HTTP {exc.code}."
            ) from exc

        except URLError as exc:
            raise CallsignProviderError(
                f"HamDB connection failed: {exc.reason}"
            ) from exc

        except TimeoutError as exc:
            raise CallsignProviderError(
                "HamDB request timed out."
            ) from exc

        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise CallsignProviderError(
                "HamDB returned an invalid response."
            ) from exc

        return self._parse_payload(
            normalized_callsign=normalized,
            payload=payload,
        )

    def _parse_payload(
        self,
        *,
        normalized_callsign: str,
        payload: object,
    ) -> CallsignRecord | None:
        if not isinstance(payload, dict):
            raise CallsignProviderError(
                "HamDB response was not a JSON object."
            )

        hamdb = payload.get("hamdb")

        if isinstance(hamdb, dict):
            root = hamdb
        else:
            root = payload

        messages = root.get("messages", {})

        if isinstance(messages, dict):
            status = optional_text(messages.get("status"))

            if status and status.upper() == "NOT_FOUND":
                return None

        callsign_data = root.get("callsign", {})

        if not isinstance(callsign_data, dict):
            callsign_data = {}

        returned_callsign = optional_text(
            callsign_data.get("call")
            or callsign_data.get("callsign")
        )

        grid_square = optional_text(
            callsign_data.get("grid")
            or callsign_data.get("grid_square")
        )

        dxcc_entity = optional_text(
            callsign_data.get("country")
            or callsign_data.get("dxcc_entity")
        )

        return CallsignRecord(
            callsign=normalize_callsign(
                returned_callsign or normalized_callsign
            ),
            display_name=build_display_name(callsign_data),
            grid_square=(
                grid_square.upper()
                if grid_square
                else None
            ),
            dxcc_entity=dxcc_entity,
            cq_zone=optional_integer(
                callsign_data.get("cqz")
                or callsign_data.get("cq_zone")
            ),
            itu_zone=optional_integer(
                callsign_data.get("ituz")
                or callsign_data.get("itu_zone")
            ),
        )


class StubCallsignProvider:
    """Local fallback used for tests and provider failures."""

    _records = {
        "KG5FCZ": CallsignRecord(
            callsign="KG5FCZ",
            display_name="Brian",
            grid_square=None,
            dxcc_entity="United States",
            cq_zone=4,
            itu_zone=7,
        ),
        "W1AW": CallsignRecord(
            callsign="W1AW",
            display_name="ARRL Headquarters",
            grid_square="FN31PR",
            dxcc_entity="United States",
            cq_zone=5,
            itu_zone=8,
        ),
        "W1ABC": CallsignRecord(
            callsign="W1ABC",
            display_name="Test Operator",
            grid_square="FN31",
            dxcc_entity="United States",
            cq_zone=5,
            itu_zone=8,
        ),
    }

    def lookup(self, callsign: str) -> CallsignRecord | None:
        return self._records.get(normalize_callsign(callsign))


class FallbackCallsignProvider:
    """Try the primary provider, then fall back on failure."""

    def __init__(
        self,
        primary: CallsignProvider,
        fallback: CallsignProvider,
    ) -> None:
        self.primary = primary
        self.fallback = fallback

    def lookup(self, callsign: str) -> CallsignRecord | None:
        try:
            result = self.primary.lookup(callsign)
        except CallsignProviderError:
            logger.exception(
                "Primary callsign provider failed for %s",
                normalize_callsign(callsign),
            )
            return self.fallback.lookup(callsign)

        if result is not None:
            return result

        return None


def get_callsign_provider() -> CallsignProvider:
    """Construct the provider selected by application configuration."""

    provider_name = str(
        current_app.config.get(
            "CALLSIGN_PROVIDER",
            "hamdb",
        )
    ).strip().lower()

    if provider_name == "stub":
        return StubCallsignProvider()

    if provider_name != "hamdb":
        raise RuntimeError(
            f"Unsupported callsign provider: {provider_name}"
        )

    primary = HamDBCallsignProvider(
        base_url=current_app.config.get(
            "HAMDB_BASE_URL",
            "http://api.hamdb.org",
        ),
        application_name=current_app.config.get(
            "HAMDB_APPLICATION_NAME",
            "kg5fcz-web",
        ),
        timeout_seconds=float(
            current_app.config.get(
                "CALLSIGN_LOOKUP_TIMEOUT_SECONDS",
                5.0,
            )
        ),
    )

    if current_app.config.get(
        "CALLSIGN_PROVIDER_FALLBACK_ENABLED",
        True,
    ):
        return FallbackCallsignProvider(
            primary=primary,
            fallback=StubCallsignProvider(),
        )

    return primary


def lookup_callsign(callsign: str) -> CallsignRecord | None:
    """Look up normalized callsign information."""

    normalized = normalize_callsign(callsign)

    if not normalized:
        return None

    return get_callsign_provider().lookup(normalized)
