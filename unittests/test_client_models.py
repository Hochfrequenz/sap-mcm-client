"""Tests for the ModelResource using aioresponses."""

from __future__ import annotations

import re
from uuid import UUID

import pytest

from sap_mcm_client import (
    ListResponse,
    MCMAuthenticationError,
    MeasurementConceptModel,
)
from sap_mcm_client._resources import ModelResource

from .conftest import (
    BASE_URL,
    _decoded_url,
    _load_json,
    captured_requests,
    mock_client,
)

_MODELS_RE = re.compile(r".*/MeasurementConceptModels.*")

# ---------------------------------------------------------------------------
# ModelResource with mocked HTTP
# ---------------------------------------------------------------------------


class TestModelResource:
    """Tests for the ModelResource using mocked HTTP responses."""

    async def test_list_models(self) -> None:
        data = _load_json("model_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_MODELS_RE, payload=data, repeat=True)
            resource = ModelResource(client, BASE_URL)

            result = await resource.list(top=5)

        assert isinstance(result, ListResponse)
        assert len(result.items) == 2

    async def test_get_model(self) -> None:
        data = _load_json("model_get.json")
        model_id = "ffffffff-2222-2222-2222-100000000001"
        async with mock_client() as (mocked, client):
            mocked.get(_MODELS_RE, payload=data, repeat=True)
            resource = ModelResource(client, BASE_URL)

            result = await resource.get(model_id, include=["all"])
            captured = captured_requests(mocked)

        assert isinstance(result, MeasurementConceptModel)
        assert result.id == UUID(model_id)
        assert "$expand=*" in _decoded_url(captured[0])

    async def test_model_401_raises(self) -> None:
        error_data = _load_json("error_401.json")
        async with mock_client() as (mocked, client):
            mocked.get(_MODELS_RE, payload=error_data, status=401, repeat=True)
            resource = ModelResource(client, BASE_URL)

            with pytest.raises(MCMAuthenticationError):
                await resource.list()
