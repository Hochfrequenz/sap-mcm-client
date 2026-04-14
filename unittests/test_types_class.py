"""Tests for MeasurementConceptClass Pydantic model."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sap_mcm_client import (
    ClassType,
    Direction,
    Division,
    MeasurementConceptClass,
    MeteringLocationType,
)

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
