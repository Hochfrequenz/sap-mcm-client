"""Tests for MeasurementConceptClass Pydantic model."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sap_mcm_client import (
    ClassType,
    ClassTypeInfo,
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

    def test_class_type_capability_flags(self) -> None:
        """The expanded classType (MCClassTypes) exposes readOnly / deletable /
        updateable capability flags (issue #28)."""
        cls = MeasurementConceptClass.model_validate(
            {
                "id": "cccccccc-3333-4444-5555-666677778888",
                "classType": {
                    "code": "SAPTEMPLATE",
                    "name": "Template",
                    "descr": "SAP Template",
                    "readOnly": True,
                    "deletable": False,
                    "updateable": False,
                },
            }
        )
        assert isinstance(cls.class_type, ClassTypeInfo)
        assert cls.class_type.read_only is True
        assert cls.class_type.deletable is False
        assert cls.class_type.updateable is False

    def test_id_text_accepts_up_to_60_chars(self) -> None:
        """The EDMX defines idText as MaxLength=60 on the measurement concept
        class and on its nested metering locations and actors; values between
        33 and 60 characters must validate on all three (regression for the
        spec's incorrect 32/12-character limits, issue #26)."""
        long_id_text = "X" * 60
        cls = MeasurementConceptClass.model_validate(
            {
                "id": "cccccccc-3333-4444-5555-666677778888",
                "idText": long_id_text,
                "meteringLocations": [
                    {
                        "id": "11111111-aaaa-bbbb-cccc-000000000001",
                        "measurementConceptClass_id": "cccccccc-3333-4444-5555-666677778888",
                        "idText": long_id_text,
                    }
                ],
                "actors": [
                    {
                        "id": "22222222-aaaa-bbbb-cccc-000000000001",
                        "measurementConceptClass_id": "cccccccc-3333-4444-5555-666677778888",
                        "idText": long_id_text,
                    }
                ],
            }
        )
        assert cls.id_text == long_id_text
        assert cls.metering_locations is not None
        assert cls.metering_locations[0].id_text == long_id_text
        assert cls.actors is not None
        assert cls.actors[0].id_text == long_id_text
