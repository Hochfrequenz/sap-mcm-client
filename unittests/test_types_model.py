"""Tests for MeasurementConceptModel Pydantic model."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest
from pydantic import ValidationError

from sap_mcm_client import (
    ClassType,
    ConceptType,
    Direction,
    Division,
    MeasurementConceptModel,
    MeteringTaskType,
    ModelStatus,
)

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

    def test_version_max_length_is_two(self) -> None:
        """The EDMX defines MeasurementConceptModels.version as MaxLength=2;
        a 2-char value is accepted and a longer one is rejected (regression
        for the spec's overly permissive 5-character limit, issue #27)."""
        base = {"id": "ffffffff-2222-2222-2222-100000000001"}
        assert MeasurementConceptModel.model_validate({**base, "version": "99"}).version == "99"
        with pytest.raises(ValidationError):
            MeasurementConceptModel.model_validate({**base, "version": "1.2.3"})
