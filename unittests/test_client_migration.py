"""Tests for the MigrationResource (migrate, get, list_staged)."""

from __future__ import annotations

import json
from uuid import UUID

import pytest

from sap_mcm_client import (
    MCMAuthenticationError,
    MCMForbiddenError,
    MCMNotFoundError,
    MigrationInstance,
    MigrationInstanceResponse,
    MigrationResponse,
    StagedMigrationInstance,
)
from sap_mcm_client._resources import MigrationResource

from .conftest import (
    BASE_URL,
    _decoded_url,
    _json_response,
    _load_json,
    _make_http_client,
    _make_mock_transport,
)

# ===========================================================================
# MigrationResource
# ===========================================================================


class TestMigrationResource:
    def test_migrate_posts_wrapper_body(self) -> None:
        response_data = _load_json("migration_response.json")
        transport = _make_mock_transport(responses={"/migrate": _json_response(response_data, 201)})
        http_client = _make_http_client(transport)
        resource = MigrationResource(http_client, BASE_URL)

        inst = MigrationInstance(
            id=UUID("b2c3d4e5-f6a7-8901-bcde-f12345678901"),
            id_text="MIG-INST-LEGACY-001",
            description="Legacy import",
        )
        resp = resource.migrate([inst])
        assert isinstance(resp, MigrationResponse)
        assert resp.request_id == UUID("f1343cac-b0ee-42aa-af23-43b1f628f61d")

        captured = transport._captured_requests  # type: ignore[attr-defined]
        assert captured[0].method == "POST"
        url = _decoded_url(captured[0])
        assert "/odata/v4/api/migrate/v1/migrate" in url

        body = json.loads(captured[0].content)
        assert "migrationInstances" in body
        assert len(body["migrationInstances"]) == 1
        assert body["migrationInstances"][0]["idText"] == "MIG-INST-LEGACY-001"
        assert body["migrationInstances"][0]["id"] == "b2c3d4e5-f6a7-8901-bcde-f12345678901"

    def test_get_constructs_url_with_expand(self) -> None:
        response_data = _load_json("migration_instance_get.json")
        instance_id = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
        transport = _make_mock_transport(
            responses={f"/MigrationInstances({instance_id})": _json_response(response_data)}
        )
        http_client = _make_http_client(transport)
        resource = MigrationResource(http_client, BASE_URL)

        result = resource.get(instance_id, include=["all"])
        assert isinstance(result, MigrationInstanceResponse)
        assert result.id == UUID(instance_id)
        assert result.id_text == "MIG-INST-LEGACY-001"

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert f"/odata/v4/api/migrate/v1/MigrationInstances({instance_id})" in url
        assert "$expand=*" in url

    def test_get_with_specific_includes(self) -> None:
        response_data = _load_json("migration_instance_get.json")
        instance_id = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
        transport = _make_mock_transport(
            responses={f"/MigrationInstances({instance_id})": _json_response(response_data)}
        )
        resource = MigrationResource(_make_http_client(transport), BASE_URL)

        resource.get(instance_id, include=["metering_locations", "market_locations"])

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert "$expand=" in url
        assert "meteringLocations" in url
        assert "marketLocations" in url

    def test_list_staged_basic(self) -> None:
        data = _load_json("migration_staged_list.json")
        transport = _make_mock_transport(responses={"/StagedMigrationInstances": _json_response(data)})
        resource = MigrationResource(_make_http_client(transport), BASE_URL)

        result = resource.list_staged(top=10, count=True)
        assert result.count == 3
        assert len(result.items) == 3
        assert all(isinstance(item, StagedMigrationInstance) for item in result.items)

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert "/odata/v4/api/migrate/v1/StagedMigrationInstances" in url
        assert "$top=10" in url
        assert "$count=true" in url

    def test_list_staged_with_request_id_filter(self) -> None:
        data = _load_json("migration_staged_list.json")
        transport = _make_mock_transport(responses={"/StagedMigrationInstances": _json_response(data)})
        resource = MigrationResource(_make_http_client(transport), BASE_URL)

        request_id = UUID("f1343cac-b0ee-42aa-af23-43b1f628f61d")
        resource.list_staged(request_id=request_id)

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        # OData V4 Guid literals are unquoted
        assert f"requestId eq {request_id}" in url

    def test_list_staged_with_status_filter(self) -> None:
        data = _load_json("migration_staged_list.json")
        transport = _make_mock_transport(responses={"/StagedMigrationInstances": _json_response(data)})
        resource = MigrationResource(_make_http_client(transport), BASE_URL)

        resource.list_staged(status="MIGRATED")

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        # OData string literals require single quotes
        assert "status_code eq 'MIGRATED'" in url

    def test_list_staged_with_include_instance(self) -> None:
        data = _load_json("migration_staged_list.json")
        transport = _make_mock_transport(responses={"/StagedMigrationInstances": _json_response(data)})
        resource = MigrationResource(_make_http_client(transport), BASE_URL)

        resource.list_staged(include_instance=True)

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert "$expand=instance" in url

    def test_list_staged_combined_filters(self) -> None:
        data = _load_json("migration_staged_list.json")
        transport = _make_mock_transport(responses={"/StagedMigrationInstances": _json_response(data)})
        resource = MigrationResource(_make_http_client(transport), BASE_URL)

        request_id = UUID("f1343cac-b0ee-42aa-af23-43b1f628f61d")
        resource.list_staged(request_id=request_id, status="FAILED", top=5, count=True)

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert f"requestId eq {request_id}" in url
        assert "status_code eq 'FAILED'" in url
        assert " and " in url
        assert "$top=5" in url
        assert "$count=true" in url


# ===========================================================================
# Migration error propagation
# ===========================================================================


class TestMigrationErrors:
    def test_404_on_get(self) -> None:
        transport = _make_mock_transport(default_response=_json_response(_load_json("error_404.json"), 404))
        resource = MigrationResource(_make_http_client(transport), BASE_URL)
        with pytest.raises(MCMNotFoundError):
            resource.get("00000000-0000-0000-0000-000000000000")

    def test_401_on_migrate(self) -> None:
        transport = _make_mock_transport(default_response=_json_response(_load_json("error_401.json"), 401))
        resource = MigrationResource(_make_http_client(transport), BASE_URL)
        with pytest.raises(MCMAuthenticationError):
            resource.migrate([])

    def test_403_on_list_staged(self) -> None:
        transport = _make_mock_transport(default_response=_json_response(_load_json("error_403.json"), 403))
        resource = MigrationResource(_make_http_client(transport), BASE_URL)
        with pytest.raises(MCMForbiddenError):
            resource.list_staged()
