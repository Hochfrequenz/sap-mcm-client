"""Tests for Pydantic model deserialization and behavior."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest

from sap_mcm_client import (
    Address,
    Ancestor,
    ClassType,
    CodeDescription,
    ConceptType,
    Direction,
    Division,
    MarketLocationUsage,
    MeasurementConceptClass,
    MeasurementConceptInstance,
    MeasurementConceptModel,
    MeteringLocationType,
    MeteringProcedure,
    MeteringTaskType,
    ModelStatus,
    OverallStatus,
    ProcessType,
    StatusEntry,
)

# ---------------------------------------------------------------------------
# Instance parsing
# ---------------------------------------------------------------------------


class TestInstanceParsing:
    """Tests for parsing MeasurementConceptInstance from fixture data."""

    def test_parse_instance_get(self, instance_get_json: dict[str, Any]) -> None:
        """Parse the full instance_get fixture and verify top-level fields."""
        # Strip OData envelope keys the same way parse_entity does
        cleaned = {
            k: v
            for k, v in instance_get_json.items()
            if k not in ("@context", "@metadataEtag", "@odata.context", "@odata.metadataEtag")
        }
        inst = MeasurementConceptInstance.model_validate(cleaned)

        assert inst.id == UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
        assert inst.id_text == "INST-79"
        assert inst.version == "1"
        assert inst.description == "Instance Electricity Purchase - Standard - Creation process - Step by Step"

    def test_division_code_is_enum(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)
        assert inst.division_code == Division.ELECTRICITY
        assert str(inst.division_code) == "EL"
        assert isinstance(inst.division_code, Division)

    def test_overall_status_code_is_enum(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)
        assert inst.overall_status_code == OverallStatus.ACTIVE
        assert isinstance(inst.overall_status_code, OverallStatus)

    def test_measurement_model_id(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)
        assert inst.measurement_model_id == UUID("ffffffff-2222-2222-2222-100000000001")

    def test_nested_metering_locations(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)

        assert inst.metering_locations is not None
        assert len(inst.metering_locations) == 1

        melo = inst.metering_locations[0]
        assert melo.id == UUID("11111111-aaaa-bbbb-cccc-000000000001")
        assert melo.id_text == "Z1"
        assert melo.type_code == MeteringLocationType.GRID_MES
        # External-ID / device-serial aliased fields (non-FK id fields)
        assert melo.metering_location_id == "DE0001234567890000000000000012345"
        assert melo.device_serial_id == "SER-9876543210"

        # Nested metering tasks
        assert melo.metering_tasks is not None
        assert len(melo.metering_tasks) == 2
        task = melo.metering_tasks[0]
        assert task.direction_code == Direction.OUT
        assert task.type_code == MeteringTaskType.AE
        assert task.planned_metering_procedure_code == MeteringProcedure.SLP
        # OBIS register codes (plain camelCase wire format)
        assert task.planned_register_code == "1.8.x"
        assert task.register_code == "1.8.0"

    def test_nested_market_locations(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)

        assert inst.market_locations is not None
        assert len(inst.market_locations) == 1

        malo = inst.market_locations[0]
        assert malo.direction_code == Direction.OUT
        # External POD-style market location id (plain camelCase wire format).
        assert malo.market_location_id == "51111111111"
        assert malo.calculation_rules is not None
        assert len(malo.calculation_rules) == 1

        rule = malo.calculation_rules[0]
        assert rule.metering_procedure_code == MeteringProcedure.SLP
        # OBIS register codes (plain camelCase).
        assert rule.planned_register_code == "1.8.x"
        assert rule.register_code is None  # explicitly null in the fixture
        assert rule.steps is not None
        assert len(rule.steps) == 1

        assert rule.usages is not None
        assert len(rule.usages) == 3
        assert rule.usages[0].usage_code == MarketLocationUsage.GRID_USE

    def test_nested_actors(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)

        assert inst.actors is not None
        assert len(inst.actors) == 1
        actor = inst.actors[0]
        assert actor.id_text == "VB"
        assert actor.type_code == "CONSUMER"
        assert actor.direction_code == Direction.OUT

    def test_nested_addresses(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)

        assert inst.addresses is not None
        assert len(inst.addresses) == 1
        addr = inst.addresses[0]
        assert addr.id == UUID("dddddddd-aaaa-bbbb-cccc-111122223333")
        # All address wire names are now asserted; the non-FK id/code fields
        # (cityID, streetID, postalCode) carry explicit Field(alias=...) so
        # they round-trip through the wire format correctly.
        assert addr.country_code == "DE"  # country_code (OData _code suffix)
        assert addr.city_id == "WALLDORF"  # cityID (uppercase per spec)
        assert addr.city_name == "Walldorf"  # cityName
        assert addr.postal_code == "69190"  # postalCode
        assert addr.street_id == "RINGSTRASSE"  # streetID (uppercase per spec)
        assert addr.street_name == "Ringstrasse"  # streetName
        assert addr.house_number == "981"  # houseNumber
        assert addr.floor_number == "5"  # floorNumber
        assert addr.supplement == "5.Stock App 67"
        assert addr.time_zone == "CEST"  # timeZone

    def test_decimal_fields_in_metering_location(self, instance_get_json: dict[str, Any]) -> None:
        """Loss factors are serialized as strings by IEEE754Compatible mode."""
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)

        assert inst.metering_locations is not None
        melo = inst.metering_locations[0]
        assert melo.loss_transformer_supply == Decimal("0")
        assert melo.loss_line_demand == Decimal("0")
        assert isinstance(melo.loss_transformer_supply, Decimal)

    def test_decimal_fields_in_metering_task(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)

        assert inst.metering_locations is not None
        metering_tasks = inst.metering_locations[0].metering_tasks
        assert metering_tasks is not None
        task = metering_tasks[0]
        assert task.loss_factor_transformer == Decimal("1")
        assert task.loss_factor_line == Decimal("1")
        assert isinstance(task.loss_factor_transformer, Decimal)

    def test_latitude_longitude_decimal(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)

        assert inst.addresses is not None
        addr = inst.addresses[0]
        assert addr.latitude == Decimal("49.30637000")
        assert addr.longitude == Decimal("8.64236000")

    def test_change_processes(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)

        assert inst.change_processes is not None
        assert len(inst.change_processes) == 1
        cp = inst.change_processes[0]
        assert cp.process_type_code == ProcessType.CREATE
        assert cp.finished is True
        # Aliased external id fields (plain camelCase, not _id suffix)
        assert cp.external_order_id == "4711"
        assert cp.external_process_id is None
        assert cp.process_data is not None
        # subscriberId is plain camelCase, not subscriber_id
        assert cp.process_data.subscriber_id is None
        assert cp.instance_characteristics is not None
        assert len(cp.instance_characteristics) == 2
        # modelEntityId is plain camelCase, not modelEntity_id
        assert cp.instance_characteristics[0].model_entity_id == UUID(
            "bbb50001-5555-5555-5555-501010000001"
        )

    def test_status_entries(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)

        assert inst.status is not None
        assert len(inst.status) == 1
        assert inst.status[0].instance_status_code == "ACTIVE"
        assert inst.status[0].process_status_code == "COMPLETED"

    def test_parse_instance_list(self, instance_list_json: dict[str, Any]) -> None:
        items = [MeasurementConceptInstance.model_validate(item) for item in instance_list_json["value"]]
        assert len(items) == 2
        assert items[0].id_text == "INST-79"
        assert items[0].division_code == Division.ELECTRICITY
        assert items[1].id_text == "INST-80"
        assert items[1].division_code == Division.GAS
        assert items[1].overall_status_code == OverallStatus.NEW


# ---------------------------------------------------------------------------
# Class parsing
# ---------------------------------------------------------------------------


class TestClassParsing:
    """Tests for parsing MeasurementConceptClass from fixture data."""

    def test_parse_class_get(self, class_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in class_get_json.items() if k not in ("@context", "@metadataEtag")}
        cls = MeasurementConceptClass.model_validate(cleaned)

        assert cls.id == UUID("cccccccc-3333-4444-5555-666677778888")
        assert cls.id_text == "P_S"
        assert cls.name == "Feed-in with unmetered generating plant"
        assert cls.class_type_code == ClassType.CLASS
        assert cls.division_code == Division.ELECTRICITY

    def test_expanded_navigation_properties(self, class_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in class_get_json.items() if k not in ("@context", "@metadataEtag")}
        cls = MeasurementConceptClass.model_validate(cleaned)

        assert cls.class_type is not None
        assert cls.class_type.code == "CLASS"
        assert cls.class_type.name == "Class"

        assert cls.division is not None
        assert cls.division.code == "EL"
        assert cls.division.name == "Electricity"

    def test_nested_metering_locations(self, class_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in class_get_json.items() if k not in ("@context", "@metadataEtag")}
        cls = MeasurementConceptClass.model_validate(cleaned)

        assert cls.metering_locations is not None
        assert len(cls.metering_locations) == 2
        assert cls.metering_locations[0].type_code == MeteringLocationType.GRID_MES
        assert cls.metering_locations[1].type_code == MeteringLocationType.GENERATOR_MES
        assert cls.metering_locations[1].optional is True

    def test_nested_actors(self, class_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in class_get_json.items() if k not in ("@context", "@metadataEtag")}
        cls = MeasurementConceptClass.model_validate(cleaned)

        assert cls.actors is not None
        assert len(cls.actors) == 2
        assert cls.actors[0].type_code == "CONSUMER"
        assert cls.actors[0].direction_code == Direction.OUT
        assert cls.actors[1].type_code == "PRODUCER"
        assert cls.actors[1].direction_code == Direction.IN
        assert cls.actors[1].energy_source_code == "SOLAR"


# ---------------------------------------------------------------------------
# Model parsing
# ---------------------------------------------------------------------------


class TestModelParsing:
    """Tests for parsing MeasurementConceptModel from fixture data."""

    def test_parse_model_get(self, model_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in model_get_json.items() if k not in ("@context", "@metadataEtag")}
        model = MeasurementConceptModel.model_validate(cleaned)

        assert model.id == UUID("ffffffff-2222-2222-2222-100000000001")
        assert model.id_text == "B_S_M1"
        assert model.name == "Standard electricity model"
        assert model.concept_type_code == ConceptType.MODEL
        assert model.status_code == ModelStatus.ACTIVE
        assert model.division_code == Division.ELECTRICITY

    def test_expanded_concept_type(self, model_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in model_get_json.items() if k not in ("@context", "@metadataEtag")}
        model = MeasurementConceptModel.model_validate(cleaned)

        assert model.concept_type is not None
        assert model.concept_type.code == "MODEL"

        assert model.status is not None
        assert model.status.code == "ACTIVE"

        assert model.division is not None
        assert model.division.code == "EL"

    def test_nested_measurement_class(self, model_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in model_get_json.items() if k not in ("@context", "@metadataEtag")}
        model = MeasurementConceptModel.model_validate(cleaned)

        assert model.measurement_class is not None
        assert model.measurement_class.id == UUID("cccccccc-3333-4444-5555-666677778888")
        assert model.measurement_class.class_type_code == ClassType.CLASS

    def test_nested_market_locations(self, model_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in model_get_json.items() if k not in ("@context", "@metadataEtag")}
        model = MeasurementConceptModel.model_validate(cleaned)

        assert model.market_locations is not None
        assert len(model.market_locations) == 1
        ml = model.market_locations[0]
        assert ml.direction_code == Direction.OUT
        assert ml.actors_mapping is not None
        assert len(ml.actors_mapping) == 1
        assert ml.calculation_rules is not None
        assert len(ml.calculation_rules) == 1

    def test_nested_model_operands(self, model_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in model_get_json.items() if k not in ("@context", "@metadataEtag")}
        model = MeasurementConceptModel.model_validate(cleaned)

        assert model.model_operands is not None
        assert len(model.model_operands) == 1
        op = model.model_operands[0]
        assert op.operand == "Z1B"
        assert op.metering_task_type_code == MeteringTaskType.AE
        assert op.metering_task_direction_code == Direction.OUT

    def test_nested_metering_location_purposes(self, model_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in model_get_json.items() if k not in ("@context", "@metadataEtag")}
        model = MeasurementConceptModel.model_validate(cleaned)

        assert model.metering_location_purposes is not None
        assert len(model.metering_location_purposes) == 1


# ---------------------------------------------------------------------------
# Model behavior: frozen, extra=ignore, serialization
# ---------------------------------------------------------------------------


class TestModelBehavior:
    """Tests for MCMBaseModel configuration."""

    def test_frozen_instance(self, instance_get_json: dict[str, Any]) -> None:
        """Frozen models reject attribute mutation."""
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)

        with pytest.raises(Exception):  # pydantic ValidationError for frozen
            inst.id_text = "CHANGED"  # type: ignore[misc]

    def test_extra_ignore(self) -> None:
        """Unknown fields are silently ignored (forward compatibility)."""
        data = {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "idText": "TEST",
            "unknownField": "should be ignored",
            "anotherNewField": 42,
        }
        # Should not raise
        inst = MeasurementConceptInstance.model_validate(data)
        assert inst.id_text == "TEST"
        # The unknown fields should not be accessible
        assert not hasattr(inst, "unknownField")

    def test_model_dump_by_alias(self, instance_get_json: dict[str, Any]) -> None:
        """model_dump(by_alias=True) produces OData wire-format field names."""
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)
        dumped = inst.model_dump(by_alias=True)

        # Verify alias format for key fields
        assert "idText" in dumped
        assert "division_code" in dumped
        assert "overallStatus_code" in dumped
        assert "measurementModel_id" in dumped
        assert "leadingGrid_code" in dumped

        # Snake_case names should NOT be present (by_alias=True means aliases only)
        assert "id_text" not in dumped
        assert "overall_status_code" not in dumped
        assert "measurement_model_id" not in dumped

    def test_model_dump_by_alias_class(self, class_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in class_get_json.items() if k not in ("@context", "@metadataEtag")}
        cls = MeasurementConceptClass.model_validate(cleaned)
        dumped = cls.model_dump(by_alias=True)

        assert "classType_code" in dumped
        assert "division_code" in dumped

    def test_populate_by_name(self) -> None:
        """Models can be constructed using Python field names (snake_case)."""
        addr = Address(
            id=UUID("dddddddd-aaaa-bbbb-cccc-111122223333"),
            country_code="DE",
            city_name="Berlin",
        )
        assert addr.country_code == "DE"
        assert addr.city_name == "Berlin"

    def test_ancestor_model(self) -> None:
        anc = Ancestor(
            id=UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890"),
            id_text="INST-79",
        )
        assert anc.id_text == "INST-79"
        dumped = anc.model_dump(by_alias=True)
        assert "idText" in dumped

    def test_status_entry_model(self) -> None:
        se = StatusEntry(
            id=UUID("eeeeeeee-4444-5555-6666-777788889999"),
            instance_status_code="ACTIVE",
            process_status_code="COMPLETED",
        )
        dumped = se.model_dump(by_alias=True)
        assert "instanceStatus_code" in dumped
        assert "processStatus_code" in dumped

    def test_code_description_model(self) -> None:
        cd = CodeDescription(code="EL", name="Electricity", descr="Electricity Division")
        assert cd.code == "EL"
        assert cd.name == "Electricity"
