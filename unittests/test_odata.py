"""Tests for the OData helper module."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import pytest

from sap_mcm_client import (
    ListResponse,
    MeasurementConceptClass,
    MeasurementConceptInstance,
    MeasurementConceptModel,
    ModelStatus,
)
from sap_mcm_client._odata import (
    CLASS_EXPAND_MAP,
    INSTANCE_EXPAND_MAP,
    MODEL_EXPAND_MAP,
    build_expand,
    build_query_params,
    parse_collection,
    parse_entity,
)

# ---------------------------------------------------------------------------
# build_expand
# ---------------------------------------------------------------------------


class TestBuildExpand:
    """Tests for the build_expand function."""

    def test_none_returns_none(self) -> None:
        assert build_expand(None) is None

    def test_empty_list_returns_none(self) -> None:
        assert build_expand([]) is None

    def test_single_include(self) -> None:
        result = build_expand(["actors"], INSTANCE_EXPAND_MAP)
        assert result == "actors"

    def test_multiple_includes(self) -> None:
        result = build_expand(["actors", "addresses"], INSTANCE_EXPAND_MAP)
        assert result == "actors,addresses"

    def test_all_returns_star(self) -> None:
        result = build_expand(["all"], INSTANCE_EXPAND_MAP)
        assert result == "*"

    def test_all_with_others_still_returns_star(self) -> None:
        """If 'all' is included, it overrides everything."""
        result = build_expand(["actors", "all"], INSTANCE_EXPAND_MAP)
        assert result == "*"

    def test_unknown_name_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Unknown include 'nonexistent'"):
            build_expand(["nonexistent"], INSTANCE_EXPAND_MAP)

    def test_instance_metering_locations_expand(self) -> None:
        result = build_expand(["metering_locations"], INSTANCE_EXPAND_MAP)
        assert result == "meteringLocations($expand=meteringTasks)"

    def test_instance_market_locations_expand(self) -> None:
        result = build_expand(["market_locations"], INSTANCE_EXPAND_MAP)
        assert result is not None
        assert "marketLocations($expand=calculationRules" in result

    def test_instance_change_processes_expand(self) -> None:
        result = build_expand(["change_processes"], INSTANCE_EXPAND_MAP)
        assert result is not None
        assert "changeProcesses" in result
        assert "processData" in result

    def test_class_expand_map_keys(self) -> None:
        result = build_expand(["metering_locations", "actors"], CLASS_EXPAND_MAP)
        assert result == "meteringLocations,actors"

    def test_class_expand_all(self) -> None:
        result = build_expand(["all"], CLASS_EXPAND_MAP)
        assert result == "*"

    def test_model_expand_map_single(self) -> None:
        result = build_expand(["model_operands"], MODEL_EXPAND_MAP)
        assert result == "modelOperands"

    def test_model_expand_market_locations(self) -> None:
        result = build_expand(["market_locations"], MODEL_EXPAND_MAP)
        assert result is not None
        assert "marketLocations" in result
        assert "calculationRules" in result

    def test_model_expand_multiple(self) -> None:
        result = build_expand(["concept_type", "status", "division"], MODEL_EXPAND_MAP)
        assert result == "conceptType,status,division"

    def test_unknown_name_in_class_map(self) -> None:
        with pytest.raises(ValueError, match="Unknown include"):
            build_expand(["nonexistent"], CLASS_EXPAND_MAP)


# ---------------------------------------------------------------------------
# build_query_params
# ---------------------------------------------------------------------------


class TestBuildQueryParams:
    """Tests for the build_query_params function."""

    def test_empty_returns_empty_dict(self) -> None:
        assert build_query_params() == {}

    def test_top(self) -> None:
        params = build_query_params(top=10)
        assert params == {"$top": "10"}

    def test_skip(self) -> None:
        params = build_query_params(skip=20)
        assert params == {"$skip": "20"}

    def test_count(self) -> None:
        params = build_query_params(count=True)
        assert params == {"$count": "true"}

    def test_count_false_not_included(self) -> None:
        params = build_query_params(count=False)
        assert "$count" not in params

    def test_order_by(self) -> None:
        params = build_query_params(order_by="idText asc")
        assert params == {"$orderby": "idText asc"}

    def test_search(self) -> None:
        params = build_query_params(search="electricity")
        assert params == {"$search": "electricity"}

    def test_expand(self) -> None:
        params = build_query_params(expand="actors,addresses")
        assert params == {"$expand": "actors,addresses"}

    def test_filters_single(self) -> None:
        params = build_query_params(filters={"division_code": "EL"})
        assert params == {"$filter": "division_code eq 'EL'"}

    def test_filters_multiple(self) -> None:
        params = build_query_params(filters={"division_code": "EL", "overall_status_code": "ACTIVE"})
        assert "$filter" in params
        filter_str = params["$filter"]
        assert "division_code eq 'EL'" in filter_str
        assert "overallStatus_code eq 'ACTIVE'" in filter_str
        assert " and " in filter_str

    def test_filters_none_values_skipped(self) -> None:
        params = build_query_params(filters={"division_code": "EL", "overall_status_code": None})
        assert params == {"$filter": "division_code eq 'EL'"}

    def test_filters_all_none_no_filter_key(self) -> None:
        params = build_query_params(filters={"division_code": None, "overall_status_code": None})
        assert "$filter" not in params

    def test_combined_params(self) -> None:
        params = build_query_params(
            top=5,
            skip=10,
            count=True,
            expand="actors",
            filters={"division_code": "EL"},
        )
        assert params["$top"] == "5"
        assert params["$skip"] == "10"
        assert params["$count"] == "true"
        assert params["$expand"] == "actors"
        assert "division_code eq 'EL'" in params["$filter"]

    def test_filter_key_converted_to_odata_camel(self) -> None:
        """Filter keys in snake_case are converted via _to_odata_camel."""
        params = build_query_params(filters={"overall_status_code": "ACTIVE"})
        assert "overallStatus_code eq 'ACTIVE'" in params["$filter"]


# ---------------------------------------------------------------------------
# parse_entity
# ---------------------------------------------------------------------------


class TestParseEntity:
    """Tests for the parse_entity function."""

    def test_strips_odata_context(self, instance_get_json: dict[str, Any]) -> None:
        """OData envelope keys are removed before model construction."""
        inst = parse_entity(instance_get_json, MeasurementConceptInstance)
        assert inst.id == UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")

    def test_strips_metadata_etag(self, class_get_json: dict[str, Any]) -> None:
        cls = parse_entity(class_get_json, MeasurementConceptClass)
        assert cls.id == UUID("cccccccc-3333-4444-5555-666677778888")

    def test_model_parse_entity(self, model_get_json: dict[str, Any]) -> None:
        model = parse_entity(model_get_json, MeasurementConceptModel)
        assert model.id == UUID("ffffffff-2222-2222-2222-100000000001")


# ---------------------------------------------------------------------------
# parse_collection
# ---------------------------------------------------------------------------


class TestParseCollection:
    """Tests for the parse_collection function."""

    def test_parses_value_array(self, instance_list_json: dict[str, Any]) -> None:
        result = parse_collection(instance_list_json, MeasurementConceptInstance)
        assert len(result.items) == 2
        assert result.items[0].id_text == "INST-79"
        assert result.items[1].id_text == "INST-80"

    def test_parses_count(self, instance_list_json: dict[str, Any]) -> None:
        result = parse_collection(instance_list_json, MeasurementConceptInstance)
        assert result.count == 2

    def test_count_is_none_when_missing(self) -> None:
        data: dict[str, Any] = {"value": []}
        result = parse_collection(data, MeasurementConceptInstance)
        assert result.count is None
        assert result.items == []

    def test_class_collection(self, class_list_json: dict[str, Any]) -> None:
        result = parse_collection(class_list_json, MeasurementConceptClass)
        assert len(result.items) == 2
        assert result.count == 2

    def test_model_collection(self, model_list_json: dict[str, Any]) -> None:
        result = parse_collection(model_list_json, MeasurementConceptModel)
        assert len(result.items) == 2
        assert result.items[0].id_text == "B_S_M1"
        assert result.items[1].status_code == ModelStatus.IN_PROGRESS


# ---------------------------------------------------------------------------
# ListResponse
# ---------------------------------------------------------------------------


class TestListResponse:
    """Tests for the ListResponse dataclass."""

    def test_is_frozen(self) -> None:
        resp: ListResponse[MeasurementConceptInstance] = ListResponse(items=[], count=5)
        with pytest.raises(AttributeError):
            resp.items = []  # type: ignore[misc]
        with pytest.raises(AttributeError):
            resp.count = 10  # type: ignore[misc]

    def test_default_count_is_none(self) -> None:
        resp: ListResponse[MeasurementConceptInstance] = ListResponse(items=[])
        assert resp.count is None

    def test_items_and_count(self, instance_get_json: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in instance_get_json.items() if k not in ("@context", "@metadataEtag")}
        inst = MeasurementConceptInstance.model_validate(cleaned)
        resp: ListResponse[MeasurementConceptInstance] = ListResponse(items=[inst, inst], count=2)
        assert len(resp.items) == 2
        assert resp.count == 2
