from app.models import Station
from app.services.callsign import CallsignRecord
from app.services.station_review import build_station_review


def test_review_for_new_station():
    record = CallsignRecord(
        callsign="W1AW",
        grid_square="FN31PR",
        dxcc_entity="United States",
    )

    items = build_station_review(None, record)
    fields = {item.field_name: item for item in items}

    assert fields["station_name"].proposed_value == "W1AW Station"
    assert fields["grid_square"].proposed_value == "FN31PR"
    assert fields["dxcc_entity"].proposed_value == "United States"


def test_review_compares_existing_values():
    station = Station(
        station_name="Home",
        grid_square="EM20",
        dxcc_entity="United States",
    )

    record = CallsignRecord(
        callsign="W1AW",
        grid_square="FN31PR",
        dxcc_entity="United States",
    )

    items = build_station_review(station, record)
    fields = {item.field_name: item for item in items}

    assert fields["station_name"].changed is True
    assert fields["grid_square"].changed is True
    assert fields["dxcc_entity"].changed is False


def test_missing_lookup_value_is_not_applicable():
    record = CallsignRecord(
        callsign="KG5FCZ",
        grid_square=None,
        dxcc_entity=None,
    )

    items = build_station_review(None, record)
    fields = {item.field_name: item for item in items}

    assert fields["grid_square"].applicable is False
    assert fields["dxcc_entity"].applicable is False
