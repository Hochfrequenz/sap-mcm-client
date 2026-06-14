"""Tests for the ClassResource using aioresponses."""

from __future__ import annotations

import re
from uuid import UUID

from sap_mcm_client import (
    Division,
    ListResponse,
    MeasurementConceptClass,
)
from sap_mcm_client._resources import ClassResource

from .conftest import (
    BASE_URL,
    _decoded_url,
    _load_json,
    captured_requests,
    mock_client,
)

_CLASSES_RE = re.compile(r".*/MeasurementConceptClasses.*")

# ---------------------------------------------------------------------------
# ClassResource with mocked HTTP
# ---------------------------------------------------------------------------


class TestClassResource:
    """Tests for the ClassResource using mocked HTTP responses."""

    async def test_list_classes(self) -> None:
        data = _load_json("class_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_CLASSES_RE, payload=data, repeat=True)
            resource = ClassResource(client, BASE_URL)

            result = await resource.list(count=True)

        assert isinstance(result, ListResponse)
        assert len(result.items) == 2
        assert result.count == 2

    async def test_get_class(self) -> None:
        data = _load_json("class_get.json")
        class_id = "cccccccc-3333-4444-5555-666677778888"
        async with mock_client() as (mocked, client):
            mocked.get(_CLASSES_RE, payload=data, repeat=True)
            resource = ClassResource(client, BASE_URL)

            result = await resource.get(class_id, include=["metering_locations", "actors"])

        assert isinstance(result, MeasurementConceptClass)
        assert result.id == UUID(class_id)

    async def test_list_classes_with_division_filter(self) -> None:
        data = _load_json("class_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_CLASSES_RE, payload=data, repeat=True)
            resource = ClassResource(client, BASE_URL)

            await resource.list(division=Division.ELECTRICITY)
            captured = captured_requests(mocked)

        url_str = _decoded_url(captured[0])
        assert "division_code" in url_str
        assert "EL" in url_str
