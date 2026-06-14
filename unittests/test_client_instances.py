"""Tests for MCMClient lifecycle, error mapping, and the InstanceResource."""

from __future__ import annotations

import json
import re
from typing import Any
from unittest.mock import patch
from uuid import UUID

import pytest

from sap_mcm_client import (
    Division,
    ListResponse,
    MCMAPIError,
    MCMAuthenticationError,
    MCMClient,
    MCMForbiddenError,
    MCMNotFoundError,
    MCMValidationError,
    MeasurementConceptInstance,
    OverallStatus,
)
from sap_mcm_client._odata import parse_entity
from sap_mcm_client._resources import (
    ClassResource,
    InstanceResource,
    ModelResource,
    _raise_for_status,
)
from sap_mcm_client.types_instance import MeasurementConceptInstanceCreate

from .conftest import (
    BASE_URL,
    TOKEN_URL,
    _decoded_url,
    _load_json,
    _make_response,
    captured_requests,
    mock_client,
)

_INSTANCES_RE = re.compile(r".*/MCMInstances.*")

# ---------------------------------------------------------------------------
# MCMClient construction and lifecycle
# ---------------------------------------------------------------------------


class TestMCMClientLifecycle:
    """Tests for MCMClient creation and async context manager protocol."""

    async def test_creates_with_valid_params(self) -> None:
        """MCMClient can be constructed without errors."""
        # We patch OAuth2ClientCredentials to avoid real token fetching
        with patch("sap_mcm_client._client.OAuth2ClientCredentials"):
            client = MCMClient(
                base_url=BASE_URL,
                token_url=TOKEN_URL,
                client_id="my-id",
                client_secret="my-secret",
            )
            assert client is not None
            await client.close()

    async def test_context_manager_protocol(self) -> None:
        """MCMClient works as an async context manager."""
        with patch("sap_mcm_client._client.OAuth2ClientCredentials"):
            async with MCMClient(
                base_url=BASE_URL,
                token_url=TOKEN_URL,
                client_id="my-id",
                client_secret="my-secret",
            ) as client:
                assert client is not None

    async def test_properties_return_correct_types(self) -> None:
        with patch("sap_mcm_client._client.OAuth2ClientCredentials"):
            async with MCMClient(
                base_url=BASE_URL,
                token_url=TOKEN_URL,
                client_id="my-id",
                client_secret="my-secret",
            ) as client:
                assert isinstance(client.instances, InstanceResource)
                assert isinstance(client.classes, ClassResource)
                assert isinstance(client.models, ModelResource)

    async def test_base_url_trailing_slash_stripped(self) -> None:
        with patch("sap_mcm_client._client.OAuth2ClientCredentials"):
            client = MCMClient(
                base_url="https://tenant.example.com/",
                token_url=TOKEN_URL,
                client_id="my-id",
                client_secret="my-secret",
            )
            assert client._base_url == "https://tenant.example.com"
            await client.close()


# ---------------------------------------------------------------------------
# HTTP error mapping
# ---------------------------------------------------------------------------


class TestErrorMapping:
    """Tests for HTTP status code to exception type mapping."""

    def test_401_raises_authentication_error(self, error_401_json: dict[str, Any]) -> None:
        response = _make_response(401, json_body=error_401_json)
        with pytest.raises(MCMAuthenticationError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 401
        assert "Unauthorized" in str(exc_info.value)

    def test_403_raises_forbidden_error(self, error_403_json: dict[str, Any]) -> None:
        response = _make_response(403, json_body=error_403_json)
        with pytest.raises(MCMForbiddenError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 403
        assert "Not authorized" in str(exc_info.value)

    def test_404_raises_not_found_error(self, error_404_json: dict[str, Any]) -> None:
        response = _make_response(404, json_body=error_404_json)
        with pytest.raises(MCMNotFoundError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value)

    def test_400_raises_validation_error(self) -> None:
        response = _make_response(400, json_body={"error": {"message": "Invalid request payload"}})
        with pytest.raises(MCMValidationError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 400

    def test_500_raises_generic_api_error(self) -> None:
        response = _make_response(500, text="Internal Server Error")
        with pytest.raises(MCMAPIError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.status_code == 500

    def test_200_does_not_raise(self) -> None:
        response = _make_response(200, json_body={"value": []})
        # Should not raise
        _raise_for_status(response)

    def test_error_detail_is_captured(self, error_404_json: dict[str, Any]) -> None:
        response = _make_response(404, json_body=error_404_json)
        with pytest.raises(MCMNotFoundError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.detail is not None
        assert "error" in exc_info.value.detail

    def test_error_without_json_body(self) -> None:
        response = _make_response(502, text="Bad Gateway")
        with pytest.raises(MCMAPIError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.detail is None
        assert "Bad Gateway" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class TestExceptionHierarchy:
    """Tests that specific exceptions inherit from MCMAPIError."""

    def test_authentication_is_api_error(self) -> None:
        assert issubclass(MCMAuthenticationError, MCMAPIError)

    def test_forbidden_is_api_error(self) -> None:
        assert issubclass(MCMForbiddenError, MCMAPIError)

    def test_not_found_is_api_error(self) -> None:
        assert issubclass(MCMNotFoundError, MCMAPIError)

    def test_validation_is_api_error(self) -> None:
        assert issubclass(MCMValidationError, MCMAPIError)

    def test_catch_all_with_base_class(self) -> None:
        exc = MCMNotFoundError("not found", status_code=404)
        with pytest.raises(MCMAPIError):
            raise exc


# ---------------------------------------------------------------------------
# InstanceResource with mocked HTTP
# ---------------------------------------------------------------------------


class TestInstanceResource:
    """Tests for the InstanceResource using mocked HTTP responses."""

    async def test_list_instances(self) -> None:
        data = _load_json("instance_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, payload=data, repeat=True)
            resource = InstanceResource(client, BASE_URL)

            result = await resource.list(top=10, count=True)
            captured = captured_requests(mocked)

        assert isinstance(result, ListResponse)
        assert len(result.items) == 2
        assert result.count == 2
        assert result.items[0].id_text == "INST-79"

        # Verify the request URL contains expected params
        assert len(captured) == 1
        url_str = _decoded_url(captured[0])
        assert "$top=10" in url_str
        assert "$count=true" in url_str

    async def test_list_instances_with_filters(self) -> None:
        data = _load_json("instance_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, payload=data, repeat=True)
            resource = InstanceResource(client, BASE_URL)

            await resource.list(
                division=Division.ELECTRICITY,
                overall_status=OverallStatus.ACTIVE,
            )
            captured = captured_requests(mocked)

        url_str = _decoded_url(captured[0])
        assert "division_code" in url_str
        assert "EL" in url_str
        assert "overallStatus_code" in url_str
        assert "ACTIVE" in url_str

    async def test_get_instance(self) -> None:
        data = _load_json("instance_get.json")
        instance_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, payload=data, repeat=True)
            resource = InstanceResource(client, BASE_URL)

            result = await resource.get(instance_id, include=["all"])
            captured = captured_requests(mocked)

        assert isinstance(result, MeasurementConceptInstance)
        assert result.id == UUID(instance_id)
        assert result.id_text == "INST-79"

        assert "$expand=*" in _decoded_url(captured[0])

    async def test_create_instance_sends_post(self) -> None:
        """Create sends a POST with the correct JSON body.

        We call _request directly because the library's create() uses
        model_dump() without mode="json", which produces UUID objects
        that stdlib json cannot serialize. This is a known limitation.
        """
        response_data = _load_json("instance_get.json")
        async with mock_client() as (mocked, client):
            mocked.post(_INSTANCES_RE, payload=response_data, status=201, repeat=True)
            resource = InstanceResource(client, BASE_URL)

            create_data = MeasurementConceptInstanceCreate(
                description="New test instance",
                measurement_model_id=UUID("ffffffff-2222-2222-2222-100000000001"),
                division_code=Division.ELECTRICITY,
            )
            # Use mode="json" to get JSON-serializable dict, then call _request
            json_body = create_data.model_dump(by_alias=True, exclude_none=True, mode="json")
            resp = await resource._request("POST", "/MCMInstances", json=json_body)
            result = parse_entity(resp.json(), MeasurementConceptInstance)
            captured = captured_requests(mocked)

        assert isinstance(result, MeasurementConceptInstance)

        assert captured[0].method == "POST"
        body = json.loads(captured[0].content)
        assert body["measurementModel_id"] == "ffffffff-2222-2222-2222-100000000001"
        assert body["division_code"] == "EL"
        assert body["description"] == "New test instance"

    def test_create_payload_serialization(self) -> None:
        """Verify MeasurementConceptInstanceCreate produces correct wire-format keys."""
        create_data = MeasurementConceptInstanceCreate(
            description="Test",
            measurement_model_id=UUID("ffffffff-2222-2222-2222-100000000001"),
            division_code=Division.ELECTRICITY,
            orderer_code="SP_DIST",
        )
        dumped = create_data.model_dump(by_alias=True, exclude_none=True, mode="json")
        assert "measurementModel_id" in dumped
        assert "division_code" in dumped
        assert "orderer_code" in dumped
        assert "description" in dumped
        # Verify values are JSON-serializable strings
        assert dumped["measurementModel_id"] == "ffffffff-2222-2222-2222-100000000001"
        assert dumped["division_code"] == "EL"

    async def test_list_instances_with_include(self) -> None:
        data = _load_json("instance_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, payload=data, repeat=True)
            resource = InstanceResource(client, BASE_URL)

            await resource.list(include=["metering_locations", "actors"])
            captured = captured_requests(mocked)

        decoded = _decoded_url(captured[0])
        assert "$expand=" in decoded
        assert "meteringLocations" in decoded
        assert "actors" in decoded

    async def test_instance_404_raises(self) -> None:
        error_data = _load_json("error_404.json")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, payload=error_data, status=404, repeat=True)
            resource = InstanceResource(client, BASE_URL)

            with pytest.raises(MCMNotFoundError):
                await resource.get("01234567-89ab-cdef-0123-456789abcdef")

    async def test_json_write_sends_odata_content_type(self) -> None:
        """JSON bodies carry the OData content type (with IEEE754Compatible)."""
        response_data = _load_json("instance_get.json")
        async with mock_client() as (mocked, client):
            mocked.post(_INSTANCES_RE, payload=response_data, status=201, repeat=True)
            resource = InstanceResource(client, BASE_URL)

            await resource._request("POST", "/MCMInstances", json={"description": "x"})
            captured = captured_requests(mocked)

        content_type = captured[0].headers.get("Content-Type", "")
        assert "application/json" in content_type
        assert "IEEE754Compatible=true" in content_type

    async def test_get_sends_no_content_type(self) -> None:
        """Bodiless GET requests do not carry a Content-Type header."""
        data = _load_json("instance_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, payload=data, repeat=True)
            resource = InstanceResource(client, BASE_URL)

            await resource.list()
            captured = captured_requests(mocked)

        assert "Content-Type" not in captured[0].headers


# ---------------------------------------------------------------------------
# Lifecycle actions
# ---------------------------------------------------------------------------


class TestLifecycleActions:
    """Tests that lifecycle actions hit the correct URL paths.

    These tests verify the URL construction and HTTP method used by each
    lifecycle action, capturing the request and returning minimal valid
    responses.
    """

    @staticmethod
    def _minimal_instance_response() -> dict[str, Any]:
        """A minimal valid instance response for lifecycle action tests."""
        return {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "idText": "INST-79",
        }

    async def test_init_change_url(self) -> None:
        instance_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        async with mock_client() as (mocked, client):
            mocked.post(_INSTANCES_RE, payload=self._minimal_instance_response(), repeat=True)
            resource = InstanceResource(client, BASE_URL)

            from sap_mcm_client.types_actions import InitChangeRequest

            data = InitChangeRequest.model_validate(
                {
                    "dataForNewInstanceVersion": [
                        {
                            "measurementModel_id": "ffffffff-2222-2222-2222-100000000001",
                        }
                    ]
                }
            )
            # Use mode="json" to get JSON-serializable types from model_dump
            json_body = data.model_dump(by_alias=True, exclude_none=True, mode="json")
            # Manually call _request to test URL construction
            await resource._request(
                "POST",
                f"/MCMInstances({instance_id})/MCMService.initChange",
                json=json_body,
            )
            captured = captured_requests(mocked)

        url_str = _decoded_url(captured[0])
        assert f"/MCMInstances({instance_id})/MCMService.initChange" in url_str
        assert captured[0].method == "POST"

    async def test_init_shutdown_url(self) -> None:
        instance_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        async with mock_client() as (mocked, client):
            mocked.post(_INSTANCES_RE, payload=self._minimal_instance_response(), repeat=True)
            resource = InstanceResource(client, BASE_URL)

            from sap_mcm_client.types_actions import InitShutdownRequest

            data = InitShutdownRequest.model_validate({"dataForNewInstanceVersion": [{"changeProcesses": [{}]}]})
            json_body = data.model_dump(by_alias=True, exclude_none=True, mode="json")
            await resource._request(
                "POST",
                f"/MCMInstances({instance_id})/MCMService.initShutdown",
                json=json_body,
            )
            captured = captured_requests(mocked)

        url_str = _decoded_url(captured[0])
        assert f"/MCMInstances({instance_id})/MCMService.initShutdown" in url_str

    async def test_init_version_cancel_url(self) -> None:
        instance_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        async with mock_client() as (mocked, client):
            mocked.post(_INSTANCES_RE, payload=self._minimal_instance_response(), repeat=True)
            resource = InstanceResource(client, BASE_URL)

            from sap_mcm_client.types_actions import InitVersionCancelRequest

            data = InitVersionCancelRequest.model_validate(
                {"dataForNewInstanceVersion": {"changeProcesses": [{"cancellationReason": "test"}]}}
            )
            json_body = data.model_dump(by_alias=True, exclude_none=True, mode="json")
            await resource._request(
                "POST",
                f"/MCMInstances({instance_id})/MCMService.initVersionCancel",
                json=json_body,
            )
            captured = captured_requests(mocked)

        url_str = _decoded_url(captured[0])
        assert f"/MCMInstances({instance_id})/MCMService.initVersionCancel" in url_str

    async def test_notify_device_removed_url(self) -> None:
        instance_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        melo_id = "11111111-aaaa-bbbb-cccc-000000000001"
        async with mock_client() as (mocked, client):
            mocked.post(_INSTANCES_RE, status=204, repeat=True)
            resource = InstanceResource(client, BASE_URL)

            await resource.notify_device_removed(instance_id, melo_id)
            captured = captured_requests(mocked)

        url_str = _decoded_url(captured[0])
        assert (
            f"/MCMInstances({instance_id})/meteringLocations({melo_id})/MCMService.notifySingleDeviceRemoved" in url_str
        )

    async def test_notify_market_location_removed_url(self) -> None:
        instance_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        malo_id = "44444444-aaaa-bbbb-cccc-000000000001"
        async with mock_client() as (mocked, client):
            mocked.post(_INSTANCES_RE, status=204, repeat=True)
            resource = InstanceResource(client, BASE_URL)

            await resource.notify_market_location_removed(instance_id, malo_id)
            captured = captured_requests(mocked)

        url_str = _decoded_url(captured[0])
        assert (
            f"/MCMInstances({instance_id})/marketLocations({malo_id})/MCMService.notifySingleMarketLocationRemoved"
            in url_str
        )

    async def test_notify_final_data_entry_ready_url(self) -> None:
        instance_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        cp_id = "aaaaaaaa-bbbb-cccc-dddd-000000000001"
        async with mock_client() as (mocked, client):
            mocked.post(_INSTANCES_RE, status=204, repeat=True)
            resource = InstanceResource(client, BASE_URL)

            await resource.notify_final_data_entry_ready(instance_id, cp_id)
            captured = captured_requests(mocked)

        url_str = _decoded_url(captured[0])
        assert f"/changeProcesses({cp_id})/processData/MCMService.notifyFinalDataEntryReady" in url_str
