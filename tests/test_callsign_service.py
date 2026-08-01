from app.services.callsign import lookup_callsign, normalize_callsign


def test_normalize_callsign():
    assert normalize_callsign(" kg5fcz ") == "KG5FCZ"


def test_stub_provider_finds_known_callsign(app):
    with app.app_context():
        record = lookup_callsign("w1aw")

    assert record is not None
    assert record.callsign == "W1AW"
    assert record.grid_square == "FN31PR"
    assert record.dxcc_entity == "United States"

def test_stub_provider_returns_none_for_unknown_callsign(app):
    with app.app_context():
        record = lookup_callsign("ZZ0ZZZ")

    assert record is None
