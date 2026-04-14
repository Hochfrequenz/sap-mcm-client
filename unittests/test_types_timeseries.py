"""Tests for Time Series Pydantic models (TimeSeriesDataPoint, DeleteTimeSeriesRequest)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest

from sap_mcm_client import (
    DeleteTimeSeriesRequest,
    TimeSeriesDataPoint,
)

# ---------------------------------------------------------------------------
# Time Series model parsing
# ---------------------------------------------------------------------------


class TestTimeSeriesDataPoint:
    """Verify parsing of the Time Series OData read response."""

    def test_parses_first_item(self, timeseries_data_json: dict[str, Any]) -> None:
        point = TimeSeriesDataPoint.model_validate(timeseries_data_json["value"][0])

        assert point.id == "0aa18b64-1111-4bbb-ae00-000000000001"
        assert point.import_id == "imp-20260101-0001"
        assert point.timestamp == datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
        assert point.time_zone_code == "UTC"
        assert point.created_at == datetime(2026, 1, 2, 0, 0, tzinfo=timezone.utc)
        assert point.value == Decimal("42.500")
        assert point.missing is False
        assert point.quality == "MEASURED"
        assert point.time_series_id == "123e4567-e89b-12d3-a456-426614174000"
        assert point.external_id == "1+1-1:1.29.0"

    def test_missing_value_is_null(self, timeseries_data_json: dict[str, Any]) -> None:
        """Entry [2] has ``missing=true`` and a ``null`` value."""
        point = TimeSeriesDataPoint.model_validate(timeseries_data_json["value"][2])
        assert point.missing is True
        assert point.value is None
        assert point.quality == "ESTIMATED"

    def test_parses_all_four(self, timeseries_data_json: dict[str, Any]) -> None:
        points = [TimeSeriesDataPoint.model_validate(item) for item in timeseries_data_json["value"]]
        assert len(points) == 4
        # All share the same time series ID / external ID in the fixture
        assert {p.time_series_id for p in points} == {"123e4567-e89b-12d3-a456-426614174000"}
        assert {p.external_id for p in points} == {"1+1-1:1.29.0"}

    def test_decimal_precision_preserved(self, timeseries_data_json: dict[str, Any]) -> None:
        points = [TimeSeriesDataPoint.model_validate(item) for item in timeseries_data_json["value"]]
        # The IEEE754Compatible string format preserves the fractional digits.
        assert points[0].value == Decimal("42.500")
        assert points[1].value == Decimal("43.125")
        assert points[3].value == Decimal("41.750")

    def test_roundtrip_by_alias(self, timeseries_data_json: dict[str, Any]) -> None:
        """``model_dump(by_alias=True)`` round-trips through the wire names."""
        original = timeseries_data_json["value"][0]
        point = TimeSeriesDataPoint.model_validate(original)
        dumped = point.model_dump(by_alias=True, mode="json")
        # All aliased wire keys survive the round-trip.
        for key in ("ID", "importID", "timeSeriesID", "externalID", "timeZoneCode"):
            assert key in dumped, f"expected wire key {key!r} in dumped body"


# ---------------------------------------------------------------------------
# DeleteTimeSeriesRequest validation
# ---------------------------------------------------------------------------


class TestDeleteTimeSeriesRequest:
    """The bulk-delete request must carry at least one identifier list."""

    def test_requires_uuids_or_external_ids(self) -> None:
        with pytest.raises(ValueError):
            DeleteTimeSeriesRequest(
                start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )

    def test_empty_lists_are_rejected(self) -> None:
        with pytest.raises(ValueError):
            DeleteTimeSeriesRequest(
                uuids=[],
                external_ids=[],
                start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )

    def test_accepts_uuids_only(self) -> None:
        req = DeleteTimeSeriesRequest(
            uuids=[UUID("123e4567-e89b-12d3-a456-426614174000")],
            start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
        )
        assert req.uuids is not None
        assert len(req.uuids) == 1
        assert req.external_ids is None

    def test_accepts_external_ids_only(self) -> None:
        req = DeleteTimeSeriesRequest(
            external_ids=["1+1-1:1.29.0"],
            start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
        )
        assert req.external_ids == ["1+1-1:1.29.0"]

    def test_accepts_both(self) -> None:
        req = DeleteTimeSeriesRequest(
            uuids=[UUID("123e4567-e89b-12d3-a456-426614174000")],
            external_ids=["1+1-1:1.29.0"],
            start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
        )
        assert req.uuids is not None and req.external_ids is not None

    def test_model_dump_by_alias_uses_wire_keys(self) -> None:
        req = DeleteTimeSeriesRequest(
            uuids=[UUID("123e4567-e89b-12d3-a456-426614174000")],
            external_ids=["1+1-1:1.29.0"],
            start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
        )
        dumped = req.model_dump(by_alias=True, mode="json", exclude_none=True)
        assert "uuids" in dumped
        assert "externalIds" in dumped
        assert "startTime" in dumped
        assert "endTime" in dumped
