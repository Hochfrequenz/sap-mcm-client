"""Tests for the v0.2 Pydantic models (Time Series + Migration)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest

from sap_mcm_client import (
    DeleteTimeSeriesRequest,
    MigrationInstance,
    MigrationInstanceResponse,
    MigrationResponse,
    StagedMigrationInstance,
    TimeSeriesDataPoint,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _strip_context(data: dict[str, Any]) -> dict[str, Any]:
    """Remove OData envelope keys (``@context``, ``@metadataEtag`` etc.)."""
    return {k: v for k, v in data.items() if not k.startswith("@")}


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


# ---------------------------------------------------------------------------
# MigrationResponse
# ---------------------------------------------------------------------------


class TestMigrationResponse:
    """Parse the POST /migrate response body."""

    def test_parses_request_id(self, migration_response_json: dict[str, Any]) -> None:
        cleaned = _strip_context(migration_response_json)
        resp = MigrationResponse.model_validate(cleaned)
        assert resp.request_id == UUID("f1343cac-b0ee-42aa-af23-43b1f628f61d")

    def test_by_alias_roundtrip(self, migration_response_json: dict[str, Any]) -> None:
        cleaned = _strip_context(migration_response_json)
        resp = MigrationResponse.model_validate(cleaned)
        dumped = resp.model_dump(by_alias=True, mode="json")
        assert "requestId" in dumped
        assert dumped["requestId"] == "f1343cac-b0ee-42aa-af23-43b1f628f61d"


# ---------------------------------------------------------------------------
# MigrationInstanceResponse
# ---------------------------------------------------------------------------


class TestMigrationInstanceResponseParsing:
    """Parse the expanded migration instance GET response."""

    def test_top_level_fields(self, migration_instance_get_json: dict[str, Any]) -> None:
        cleaned = _strip_context(migration_instance_get_json)
        inst = MigrationInstanceResponse.model_validate(cleaned)

        assert inst.id == UUID("b2c3d4e5-f6a7-8901-bcde-f12345678901")
        assert inst.id_text == "MIG-INST-LEGACY-001"
        assert inst.version == "1"
        assert inst.measurement_model_id == UUID("ffffffff-2222-2222-2222-100000000001")
        assert inst.description == "Migrated measurement concept instance from legacy system."
        assert inst.overwrite is False
        assert inst.modified_at is not None
        assert inst.modified_at.year == 2024

    def test_addresses_parsed(self, migration_instance_get_json: dict[str, Any]) -> None:
        cleaned = _strip_context(migration_instance_get_json)
        inst = MigrationInstanceResponse.model_validate(cleaned)
        assert inst.addresses is not None
        assert len(inst.addresses) == 1
        addr = inst.addresses[0]
        assert addr.country_code == "DE"
        # Aliased id/code fields that don't follow the OData _suffix pattern
        # (spec uses uppercase ID + plain camelCase for postalCode).
        assert addr.city_id == "WALLDORF"
        assert addr.city_name == "Walldorf"
        assert addr.postal_code == "69190"
        assert addr.street_id == "RINGSTRASSE"
        assert addr.street_name == "Ringstrasse"
        assert addr.latitude == Decimal("49.30637000")
        assert addr.longitude == Decimal("8.64236000")

    def test_metering_locations_with_altitude_and_tasks(self, migration_instance_get_json: dict[str, Any]) -> None:
        cleaned = _strip_context(migration_instance_get_json)
        inst = MigrationInstanceResponse.model_validate(cleaned)
        assert inst.metering_locations is not None
        assert len(inst.metering_locations) == 1
        melo = inst.metering_locations[0]
        # idText is migration-specific (up to 60 chars)
        assert melo.id_text == "Migrated Metering Location Z1 (legacy)"
        # altitude is migration-specific
        assert melo.altitude == Decimal("125.500")
        # Aliased non-FK id fields (plain camelCase per spec).
        assert melo.metering_location_id == "DE0001234567890000000000000012345"
        assert melo.device_serial_id == "SER-9876543210"
        assert melo.metering_tasks is not None
        assert len(melo.metering_tasks) == 1
        task = melo.metering_tasks[0]
        # plannedMeteringProcedure_code is migration-specific
        assert str(task.planned_metering_procedure_code) == "SLP"
        assert task.direction_code is not None
        assert str(task.direction_code) == "OUT"
        # OBIS register codes (plain camelCase).
        assert task.planned_register_code == "1.8.x"
        assert task.register_code == "1.8.0"

    def test_market_locations_with_calculation_rules(self, migration_instance_get_json: dict[str, Any]) -> None:
        cleaned = _strip_context(migration_instance_get_json)
        inst = MigrationInstanceResponse.model_validate(cleaned)
        assert inst.market_locations is not None
        assert len(inst.market_locations) == 1
        malo = inst.market_locations[0]
        assert malo.id_text == "Migrated Market Location VB (legacy)"
        # Aliased non-FK market location id (plain camelCase per spec).
        assert malo.market_location_id == "51111111111"
        assert malo.calculation_rules is not None
        rule = malo.calculation_rules[0]
        assert rule.expression == "Z1B"
        # OBIS register codes (plain camelCase).
        assert rule.planned_register_code == "1.8.x"
        assert rule.usages is not None
        assert len(rule.usages) == 2
        assert malo.actors_mapping is not None
        assert len(malo.actors_mapping) == 1

    def test_actors_migration_specific_fields(self, migration_instance_get_json: dict[str, Any]) -> None:
        cleaned = _strip_context(migration_instance_get_json)
        inst = MigrationInstanceResponse.model_validate(cleaned)
        assert inst.actors is not None
        assert len(inst.actors) == 1
        actor = inst.actors[0]
        # idText up to 60 chars (migration-specific)
        assert actor.id_text == "Migrated Actor VB (residential consumer)"
        # subType_code is a migration-specific field (_code suffix keyed)
        assert actor.sub_type_code == "RESID"
        # installationDate / commercialSetupDate alias correctly
        assert actor.installation_date is not None
        assert actor.installation_date.year == 2024
        assert actor.commercial_setup_date is not None
        assert actor.commercial_setup_date.year == 2024
        # externalActorId is plain camelCase (not externalActor_id).
        assert actor.external_actor_id == "LEGACY-ACT-0815"

    def test_status_and_change_processes(self, migration_instance_get_json: dict[str, Any]) -> None:
        cleaned = _strip_context(migration_instance_get_json)
        inst = MigrationInstanceResponse.model_validate(cleaned)
        assert inst.status is not None
        assert inst.status.instance_status_code == "ACTIVE"
        assert inst.status.process_status_code == "COMPLETED"
        assert inst.change_processes is not None
        assert len(inst.change_processes) == 1
        cp = inst.change_processes[0]
        assert str(cp.process_type_code) == "CREATE"
        assert cp.finished is True
        assert cp.modified_at is not None
        assert cp.modified_at.year == 2024
        # Aliased external order/process ids (plain camelCase).
        assert cp.external_order_id == "LEGACY-ORD-4711"
        assert cp.external_process_id == "LEGACY-PROC-0815"

    def test_operand_mappings(self, migration_instance_get_json: dict[str, Any]) -> None:
        cleaned = _strip_context(migration_instance_get_json)
        inst = MigrationInstanceResponse.model_validate(cleaned)
        assert inst.operand_mappings is not None
        assert len(inst.operand_mappings) == 1
        om = inst.operand_mappings[0]
        assert om.operand == "Z1B"
        assert om.metering_task_id == UUID("33333333-aaaa-bbbb-cccc-000000000001")


# ---------------------------------------------------------------------------
# StagedMigrationInstance list parsing
# ---------------------------------------------------------------------------


class TestStagedMigrationInstanceParsing:
    """Parse entries from the StagedMigrationInstances collection."""

    def test_all_three_entries(self, migration_staged_list_json: dict[str, Any]) -> None:
        entries = [StagedMigrationInstance.model_validate(item) for item in migration_staged_list_json["value"]]
        assert len(entries) == 3
        assert {e.status_code for e in entries} == {"MIGRATED", "FAILED", "RECEIVED"}

    def test_migrated_entry(self, migration_staged_list_json: dict[str, Any]) -> None:
        entry = StagedMigrationInstance.model_validate(migration_staged_list_json["value"][0])
        assert entry.id == UUID("aa000001-1111-2222-3333-444455556666")
        assert entry.id_text == "STAGED-2026-02-01-01"
        assert entry.status_code == "MIGRATED"
        assert entry.request_id == UUID("f1343cac-b0ee-42aa-af23-43b1f628f61d")
        assert entry.instance_overall_status_code is not None
        assert str(entry.instance_overall_status_code) == "ACTIVE"
        assert entry.time_migration_duration == "00:02:40"

    def test_failed_entry_has_status_reason(self, migration_staged_list_json: dict[str, Any]) -> None:
        entry = StagedMigrationInstance.model_validate(migration_staged_list_json["value"][1])
        assert entry.status_code == "FAILED"
        assert entry.status_reason is not None
        assert "Validation error" in entry.status_reason
        assert entry.overwrite is True
        assert entry.instance_data is not None  # raw JSON kept until success

    def test_received_entry_has_no_migration_end(self, migration_staged_list_json: dict[str, Any]) -> None:
        entry = StagedMigrationInstance.model_validate(migration_staged_list_json["value"][2])
        assert entry.status_code == "RECEIVED"
        assert entry.time_migration_start is None
        assert entry.time_migration_end is None

    def test_by_alias_dump_uses_request_id_wire_name(self, migration_staged_list_json: dict[str, Any]) -> None:
        entry = StagedMigrationInstance.model_validate(migration_staged_list_json["value"][0])
        dumped = entry.model_dump(by_alias=True, mode="json", exclude_none=True)
        assert "requestId" in dumped
        assert dumped["requestId"] == "f1343cac-b0ee-42aa-af23-43b1f628f61d"


# ---------------------------------------------------------------------------
# MigrationInstance (request body) roundtrip
# ---------------------------------------------------------------------------


class TestMigrationInstanceRoundtrip:
    """Parse the migration_instance_get fixture as a MigrationInstance request body."""

    def test_roundtrip_dumps_wire_keys(self, migration_instance_get_json: dict[str, Any]) -> None:
        cleaned = _strip_context(migration_instance_get_json)
        # MigrationInstance is the request model (input); it shares most fields with the response.
        # We construct via keyword args to be robust against the response carrying
        # response-only fields (overallStatus_code, status_id, modifiedAt, status).
        inst = MigrationInstance(
            id=UUID(cleaned["id"]),
            id_text=cleaned["idText"],
            version=cleaned["version"],
            measurement_model_id=UUID(cleaned["measurementModel_id"]),
            division_code=cleaned["division_code"],
            description=cleaned["description"],
            overwrite=True,
        )
        dumped = inst.model_dump(by_alias=True, mode="json", exclude_none=True)
        # All wire keys use the migration naming
        assert dumped["id"] == str(inst.id)
        assert dumped["idText"] == "MIG-INST-LEGACY-001"
        assert dumped["measurementModel_id"] == "ffffffff-2222-2222-2222-100000000001"
        assert dumped["division_code"] == "EL"
        assert dumped["overwrite"] is True
