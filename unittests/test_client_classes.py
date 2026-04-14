"""Tests for the ClassResource using mock HTTP transport."""

from __future__ import annotations

from uuid import UUID

from sap_mcm_client import (
    Division,
    ListResponse,
    MeasurementConceptClass,
)
from sap_mcm_client._resources import ClassResource

from .conftest import (
    _decoded_url,
    _json_response,
    _load_json,
    _make_client_with_transport,
    _make_mock_transport,
)

# ---------------------------------------------------------------------------
# ClassResource with mock transport
# ---------------------------------------------------------------------------


class TestClassResource:
    """Tests for the ClassResource using mock HTTP transport."""

    def test_list_classes(self) -> None:
        data = _load_json("class_list.json")
        transport = _make_mock_transport(responses={"/MeasurementConceptClasses": _json_response(data)})
        http_client, base_url = _make_client_with_transport(transport)
        resource = ClassResource(http_client, base_url)

        result = resource.list(count=True)

        assert isinstance(result, ListResponse)
        assert len(result.items) == 2
        assert result.count == 2

    def test_get_class(self) -> None:
        data = _load_json("class_get.json")
        class_id = "cccccccc-3333-4444-5555-666677778888"
        transport = _make_mock_transport(responses={f"/MeasurementConceptClasses({class_id})": _json_response(data)})
        http_client, base_url = _make_client_with_transport(transport)
        resource = ClassResource(http_client, base_url)

        result = resource.get(class_id, include=["metering_locations", "actors"])

        assert isinstance(result, MeasurementConceptClass)
        assert result.id == UUID(class_id)

    def test_list_classes_with_division_filter(self) -> None:
        data = _load_json("class_list.json")
        transport = _make_mock_transport(responses={"/MeasurementConceptClasses": _json_response(data)})
        http_client, base_url = _make_client_with_transport(transport)
        resource = ClassResource(http_client, base_url)

        resource.list(division=Division.ELECTRICITY)

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url_str = _decoded_url(captured[0])
        assert "division_code" in url_str
        assert "EL" in url_str
