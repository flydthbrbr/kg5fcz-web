from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CallsignRecord:
    """Normalized amateur-radio callsign information."""

    callsign: str
    display_name: str | None = None
    grid_square: str | None = None
    dxcc_entity: str | None = None
    cq_zone: int | None = None
    itu_zone: int | None = None


class CallsignProvider(Protocol):
    """Interface implemented by callsign-data providers."""

    def lookup(self, callsign: str) -> CallsignRecord | None:
        """Return a normalized record or None when not found."""


class StubCallsignProvider:
    """
    Local development provider.

    Replace this provider later with QRZ, HamQTH, FCC, or another
    external service without changing routes or templates.
    """

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
        normalized = normalize_callsign(callsign)
        return self._records.get(normalized)


def normalize_callsign(callsign: str) -> str:
    """Normalize a callsign before passing it to a provider."""

    return callsign.strip().upper()


def get_callsign_provider() -> CallsignProvider:
    """
    Return the configured lookup provider.

    The first implementation always uses the local stub provider.
    """

    return StubCallsignProvider()


def lookup_callsign(callsign: str) -> CallsignRecord | None:
    """Look up and normalize callsign information."""

    normalized = normalize_callsign(callsign)

    if not normalized:
        return None

    provider = get_callsign_provider()
    return provider.lookup(normalized)
