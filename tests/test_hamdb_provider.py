from app.services.callsign import HamDBCallsignProvider


def provider():
    return HamDBCallsignProvider(
        base_url="http://example.invalid",
        application_name="kg5fcz-tests",
        timeout_seconds=1.0,
    )


def test_hamdb_parser_normalizes_record():
    payload = {
        "hamdb": {
            "callsign": {
                "call": "w1aw",
                "fname": "ARRL",
                "name": "Headquarters",
                "grid": "fn31pr",
                "country": "United States",
                "cqz": "5",
                "ituz": "8",
            },
            "messages": {
                "status": "OK",
            },
        },
    }

    record = provider()._parse_payload(
        normalized_callsign="W1AW",
        payload=payload,
    )

    assert record is not None
    assert record.callsign == "W1AW"
    assert record.display_name == "ARRL Headquarters"
    assert record.grid_square == "FN31PR"
    assert record.dxcc_entity == "United States"
    assert record.cq_zone == 5
    assert record.itu_zone == 8


def test_hamdb_parser_returns_none_when_not_found():
    payload = {
        "hamdb": {
            "messages": {
                "status": "NOT_FOUND",
            },
        },
    }

    record = provider()._parse_payload(
        normalized_callsign="ZZ0ZZZ",
        payload=payload,
    )

    assert record is None


def test_hamdb_parser_handles_missing_optional_fields():
    payload = {
        "hamdb": {
            "callsign": {
                "call": "W1AW",
            },
            "messages": {
                "status": "OK",
            },
        },
    }

    record = provider()._parse_payload(
        normalized_callsign="W1AW",
        payload=payload,
    )

    assert record is not None
    assert record.callsign == "W1AW"
    assert record.display_name is None
    assert record.grid_square is None
    assert record.cq_zone is None
    assert record.itu_zone is None

from app.services.callsign import (
    CallsignProviderError,
    CallsignRecord,
    FallbackCallsignProvider,
)


class FailingProvider:
    def lookup(self, callsign):
        raise CallsignProviderError("Provider unavailable")


class KnownFallbackProvider:
    def lookup(self, callsign):
        return CallsignRecord(
            callsign=callsign,
            grid_square="EM20",
        )


def test_fallback_provider_is_used_after_primary_failure():
    combined = FallbackCallsignProvider(
        primary=FailingProvider(),
        fallback=KnownFallbackProvider(),
    )

    record = combined.lookup("KG5FCZ")

    assert record is not None
    assert record.callsign == "KG5FCZ"
    assert record.grid_square == "EM20"

