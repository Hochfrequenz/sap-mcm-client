"""Tests for the MigrationResource (migrate, get, list_staged)."""

from __future__ import annotations

import json
import re
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
    _load_json,
    captured_requests,
    mock_client,
)

_MIGRATE_RE = re.compile(r".*/v1/migrate.*")
_MIGRATION_INSTANCES_RE = re.compile(r".*/MigrationInstances.*")
_STAGED_RE = re.compile(r".*/StagedMigrationInstances.*")
_PURGE_RE = re.compile(r".*/purge.*")
_CHANGE_PROCESSES_RE = re.compile(r".*/MIGChangeProcesses.*")

# ===========================================================================
# MigrationResource
# ===========================================================================


class TestMigrationResource:
    async def test_migrate_posts_wrapper_body(self) -> None:
        response_data = _load_json("migration_response.json")
        async with mock_client() as (mocked, client):
            mocked.post(_MIGRATE_RE, payload=response_data, status=201, repeat=True)
            resource = MigrationResource(client, BASE_URL)

            inst = MigrationInstance(
                id=UUID("b2c3d4e5-f6a7-8901-bcde-f12345678901"),
                id_text="MIG-INST-LEGACY-001",
                description="Legacy import",
            )
            resp = await resource.migrate([inst])
            captured = captured_requests(mocked)

        assert isinstance(resp, MigrationResponse)
        assert resp.request_id == UUID("f1343cac-b0ee-42aa-af23-43b1f628f61d")

        assert captured[0].method == "POST"
        url = _decoded_url(captured[0])
        assert "/odata/v4/api/migrate/v1/migrate" in url

        body = json.loads(captured[0].content)
        assert "migrationInstances" in body
        assert len(body["migrationInstances"]) == 1
        assert body["migrationInstances"][0]["idText"] == "MIG-INST-LEGACY-001"
        assert body["migrationInstances"][0]["id"] == "b2c3d4e5-f6a7-8901-bcde-f12345678901"

    async def test_get_constructs_url_with_expand(self) -> None:
        response_data = _load_json("migration_instance_get.json")
        instance_id = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
        async with mock_client() as (mocked, client):
            mocked.get(_MIGRATION_INSTANCES_RE, payload=response_data, repeat=True)
            resource = MigrationResource(client, BASE_URL)

            result = await resource.get(instance_id, include=["all"])
            captured = captured_requests(mocked)

        assert isinstance(result, MigrationInstanceResponse)
        assert result.id == UUID(instance_id)
        assert result.id_text == "MIG-INST-LEGACY-001"

        url = _decoded_url(captured[0])
        assert f"/odata/v4/api/migrate/v1/MigrationInstances({instance_id})" in url
        assert "$expand=*" in url

    async def test_get_with_specific_includes(self) -> None:
        response_data = _load_json("migration_instance_get.json")
        instance_id = "b2c3d4e5-f6a7-8901-bcde-f12345678901"
        async with mock_client() as (mocked, client):
            mocked.get(_MIGRATION_INSTANCES_RE, payload=response_data, repeat=True)
            resource = MigrationResource(client, BASE_URL)

            await resource.get(instance_id, include=["metering_locations", "market_locations"])
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert "$expand=" in url
        assert "meteringLocations" in url
        assert "marketLocations" in url

    async def test_list_staged_basic(self) -> None:
        data = _load_json("migration_staged_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_STAGED_RE, payload=data, repeat=True)
            resource = MigrationResource(client, BASE_URL)

            result = await resource.list_staged(top=10, count=True)
            captured = captured_requests(mocked)

        assert result.count == 3
        assert len(result.items) == 3
        assert all(isinstance(item, StagedMigrationInstance) for item in result.items)

        url = _decoded_url(captured[0])
        assert "/odata/v4/api/migrate/v1/StagedMigrationInstances" in url
        assert "$top=10" in url
        assert "$count=true" in url

    async def test_list_staged_with_request_id_filter(self) -> None:
        data = _load_json("migration_staged_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_STAGED_RE, payload=data, repeat=True)
            resource = MigrationResource(client, BASE_URL)

            request_id = UUID("f1343cac-b0ee-42aa-af23-43b1f628f61d")
            await resource.list_staged(request_id=request_id)
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        # OData V4 Guid literals are unquoted
        assert f"requestId eq {request_id}" in url

    async def test_list_staged_with_status_filter(self) -> None:
        data = _load_json("migration_staged_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_STAGED_RE, payload=data, repeat=True)
            resource = MigrationResource(client, BASE_URL)

            await resource.list_staged(status="MIGRATED")
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        # OData string literals require single quotes
        assert "status_code eq 'MIGRATED'" in url

    async def test_list_staged_with_include_instance(self) -> None:
        data = _load_json("migration_staged_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_STAGED_RE, payload=data, repeat=True)
            resource = MigrationResource(client, BASE_URL)

            await resource.list_staged(include_instance=True)
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert "$expand=instance" in url

    async def test_list_staged_combined_filters(self) -> None:
        data = _load_json("migration_staged_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_STAGED_RE, payload=data, repeat=True)
            resource = MigrationResource(client, BASE_URL)

            request_id = UUID("f1343cac-b0ee-42aa-af23-43b1f628f61d")
            await resource.list_staged(request_id=request_id, status="FAILED", top=5, count=True)
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert f"requestId eq {request_id}" in url
        assert "status_code eq 'FAILED'" in url
        assert " and " in url
        assert "$top=5" in url
        assert "$count=true" in url

    async def test_purge_posts_request_id(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.post(_PURGE_RE, payload={}, status=204, repeat=True)
            resource = MigrationResource(client, BASE_URL)

            request_id = UUID("f1343cac-b0ee-42aa-af23-43b1f628f61d")
            await resource.purge(request_id)
            captured = captured_requests(mocked)

        assert captured[0].method == "POST"
        url = _decoded_url(captured[0])
        assert "/odata/v4/api/migrate/v1/purge" in url
        assert json.loads(captured[0].content) == {"requestId": str(request_id)}

    async def test_check_progress_parses_response(self) -> None:
        progress_data = {
            "changeProcessId": "aaaaaaaa-bbbb-cccc-dddd-000000000001",
            "instanceId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
            "instanceIdText": "MIG-INST-LEGACY-001",
            "instanceVersion": "1",
            "currentStatus": {"instanceStatus": "STAGED", "processStatus": "IN_PROGRESS"},
            "nextStatus": {"instanceStatus": "ACTIVE", "processStatus": "DONE"},
            "failedValidations": [{"name": "missingActor", "position": 2, "parameters": ["actor", "MELO1"]}],
        }
        async with mock_client() as (mocked, client):
            mocked.get(_MIGRATION_INSTANCES_RE, payload=progress_data, repeat=True)
            resource = MigrationResource(client, BASE_URL)

            instance_id = UUID("b2c3d4e5-f6a7-8901-bcde-f12345678901")
            progress = await resource.check_progress(instance_id)
            captured = captured_requests(mocked)

        assert captured[0].method == "GET"
        url = _decoded_url(captured[0])
        assert f"/MigrationInstances({instance_id})/MCMMigrationService.checkProgress" in url

        assert progress.instance_id == instance_id
        assert progress.instance_id_text == "MIG-INST-LEGACY-001"
        assert progress.current_status is not None
        assert progress.current_status.instance_status == "STAGED"
        assert progress.failed_validations is not None
        assert progress.failed_validations[0].name == "missingActor"
        assert progress.failed_validations[0].parameters == ["actor", "MELO1"]

    async def test_check_change_process_progress_builds_url(self) -> None:
        progress_data = {
            "changeProcessId": "aaaaaaaa-bbbb-cccc-dddd-000000000001",
            "instanceId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
            "instanceIdText": "MIG-INST-LEGACY-001",
            "instanceVersion": "1",
        }
        async with mock_client() as (mocked, client):
            mocked.get(_CHANGE_PROCESSES_RE, payload=progress_data, repeat=True)
            resource = MigrationResource(client, BASE_URL)

            change_process_id = UUID("aaaaaaaa-bbbb-cccc-dddd-000000000001")
            progress = await resource.check_change_process_progress(change_process_id)
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert f"/MIGChangeProcesses({change_process_id})/MCMMigrationService.checkProgress" in url
        assert progress.change_process_id == change_process_id


# ===========================================================================
# Migration error propagation
# ===========================================================================


class TestMigrationErrors:
    async def test_404_on_get(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.get(_MIGRATION_INSTANCES_RE, payload=_load_json("error_404.json"), status=404, repeat=True)
            resource = MigrationResource(client, BASE_URL)
            with pytest.raises(MCMNotFoundError):
                await resource.get("00000000-0000-0000-0000-000000000000")

    async def test_401_on_migrate(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.post(_MIGRATE_RE, payload=_load_json("error_401.json"), status=401, repeat=True)
            resource = MigrationResource(client, BASE_URL)
            with pytest.raises(MCMAuthenticationError):
                await resource.migrate([])

    async def test_403_on_list_staged(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.get(_STAGED_RE, payload=_load_json("error_403.json"), status=403, repeat=True)
            resource = MigrationResource(client, BASE_URL)
            with pytest.raises(MCMForbiddenError):
                await resource.list_staged()
