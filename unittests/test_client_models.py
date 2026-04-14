"""Tests for the ModelResource using mock HTTP transport."""

from __future__ import annotations

from uuid import UUID

import pytest

from sap_mcm_client import (
    ListResponse,
    MCMAuthenticationError,
    MeasurementConceptModel,
)
from sap_mcm_client._resources import ModelResource

from .conftest import (
    _decoded_url,
    _json_response,
    _load_json,
    _make_client_with_transport,
    _make_mock_transport,
)

# ---------------------------------------------------------------------------
# ModelResource with mock transport
# ---------------------------------------------------------------------------


class TestModelResource:
    """Tests for the ModelResource using mock HTTP transport."""

    def test_list_models(self) -> None:
        data = _load_json("model_list.json")
        transport = _make_mock_transport(responses={"/MeasurementConceptModels": _json_response(data)})
        http_client, base_url = _make_client_with_transport(transport)
        resource = ModelResource(http_client, base_url)

        result = resource.list(top=5)

        assert isinstance(result, ListResponse)
        assert len(result.items) == 2

    def test_get_model(self) -> None:
        data = _load_json("model_get.json")
        model_id = "ffffffff-2222-2222-2222-100000000001"
        transport = _make_mock_transport(responses={f"/MeasurementConceptModels({model_id})": _json_response(data)})
        http_client, base_url = _make_client_with_transport(transport)
        resource = ModelResource(http_client, base_url)

        result = resource.get(model_id, include=["all"])

        assert isinstance(result, MeasurementConceptModel)
        assert result.id == UUID(model_id)

        captured = transport._captured_requests  # type: ignore[attr-defined]
        assert "$expand=*" in _decoded_url(captured[0])

    def test_model_401_raises(self) -> None:
        error_data = _load_json("error_401.json")
        transport = _make_mock_transport(default_response=_json_response(error_data, 401))
        http_client, base_url = _make_client_with_transport(transport)
        resource = ModelResource(http_client, base_url)

        with pytest.raises(MCMAuthenticationError):
            resource.list()
