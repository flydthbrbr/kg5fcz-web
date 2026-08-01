from dataclasses import dataclass
from typing import Any

from app.models import Station
from app.services.callsign import CallsignRecord


@dataclass(frozen=True)
class StationReviewItem:
    """One proposed station-field change."""

    field_name: str
    label: str
    current_value: Any
    proposed_value: Any
    changed: bool
    applicable: bool


def build_station_review(
    station: Station | None,
    record: CallsignRecord,
) -> list[StationReviewItem]:
    """Compare current station data with callsign lookup data."""

    current_grid = station.grid_square if station else None
    current_dxcc = station.dxcc_entity if station else None

    items = [
        StationReviewItem(
            field_name="station_name",
            label="Station name",
            current_value=(
                station.station_name
                if station
                else None
            ),
            proposed_value=f"{record.callsign} Station",
            changed=(
                station is None
                or station.station_name
                != f"{record.callsign} Station"
            ),
            applicable=True,
        ),
        StationReviewItem(
            field_name="grid_square",
            label="Grid square",
            current_value=current_grid,
            proposed_value=record.grid_square,
            changed=current_grid != record.grid_square,
            applicable=record.grid_square is not None,
        ),
        StationReviewItem(
            field_name="dxcc_entity",
            label="DXCC entity",
            current_value=current_dxcc,
            proposed_value=record.dxcc_entity,
            changed=current_dxcc != record.dxcc_entity,
            applicable=record.dxcc_entity is not None,
        ),
    ]

    return items
