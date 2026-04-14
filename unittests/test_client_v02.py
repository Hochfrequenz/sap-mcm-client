"""Tests for the v0.2 TimeSeries and Migration resources."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from io import BytesIO
from typing import Any, cast
from urllib.parse import unquote, unquote_plus, urlsplit
from uuid import UUID

import httpx
import pytest

from sap_mcm_client import (
    DeleteTimeSeriesRequest,
    MCMAuthenticationError,
    MCMForbiddenError,
    MCMNotFoundError,
    MigrationInstance,
    MigrationInstanceResponse,
    MigrationResponse,
    StagedMigrationInstance,
    TimeSeriesDataPoint,
)
from sap_mcm_client._resources import MigrationResource, TimeSeriesResource

from .conftest import TESTDATA

BASE_URL = "https://tenant.example.com"


def _decoded_url(request: httpx.Request) -> str:
    """Return a fully percent-decoded form of the request URL.

    Only the query string is ``unquote_plus``-decoded (``+`` → space), so
    that literal ``+`` characters in the path (e.g. in an ``externalId``
    segment) survive unchanged for assertions.
    """
    parts = urlsplit(str(request.url))
    path = unquote(parts.path)
    query = unquote_plus(parts.query)
    if query:
        return f"{parts.scheme}://{parts.netloc}{path}?{query}"
    return f"{parts.scheme}://{parts.netloc}{path}"


def _load_json(name: str) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads((TESTDATA / name).read_text(encoding="utf-8")))


def _json_response(data: Any, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=data,
        request=httpx.Request("GET", "https://example.com"),
    )


def _make_mock_transport(
    responses: dict[str, httpx.Response] | None = None,
    default_response: httpx.Response | None = None,
) -> httpx.MockTransport:
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        url_str = str(request.url)
        if responses:
            for path_substr, resp in responses.items():
                if path_substr in url_str:
                    return resp
        if default_response is not None:
            return default_response
        return httpx.Response(status_code=404, request=request)

    transport = httpx.MockTransport(handler)
    transport._captured_requests = captured_requests  # type: ignore[attr-defined]
    return transport


def _make_http_client(transport: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(transport=transport)


# ===========================================================================
# TimeSeriesResource - read endpoints
# ===========================================================================


class TestTimeSeriesReadURLs:
    """Verify that get_data / get_history build the correct OData URL."""

    _TS_ID = "123e4567-e89b-12d3-a456-426614174000"
    _EXT_ID = "1+1-1:1.29.0"
    _PATH_PREFIX = "/odata/v4/api/v1/TimeSeries/"

    def _resource(self, fixture: dict[str, Any] | None = None) -> tuple[TimeSeriesResource, httpx.MockTransport]:
        data = fixture if fixture is not None else _load_json("timeseries_data.json")
        transport = _make_mock_transport(default_response=_json_response(data))
        http_client = _make_http_client(transport)
        return TimeSeriesResource(http_client, BASE_URL), transport

    def test_get_data_by_time_series_id_base(self) -> None:
        resource, transport = self._resource()
        points = resource.get_data(time_series_id=self._TS_ID)
        assert len(points) == 4
        assert isinstance(points[0], TimeSeriesDataPoint)

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert f"{self._PATH_PREFIX}getTimeSeriesDataByTimeSeriesID?" in url
        # Single-quote literal escaping for the UUID
        assert f"timeSeriesID='{self._TS_ID}'" in url
        assert "fromDate" not in url
        assert "toDate" not in url

    def test_get_data_by_time_series_id_since(self) -> None:
        resource, transport = self._resource()
        resource.get_data(time_series_id=self._TS_ID, from_date=date(2025, 2, 1))

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert "getTimeSeriesDataByTimeSeriesIDSince?" in url
        assert "fromDate='2025-02-01'" in url
        assert "toDate" not in url

    def test_get_data_by_time_series_id_in_period(self) -> None:
        resource, transport = self._resource()
        resource.get_data(
            time_series_id=self._TS_ID,
            from_date=date(2025, 2, 1),
            to_date=date(2025, 2, 28),
        )

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert "getTimeSeriesDataByTimeSeriesIDInPeriod?" in url
        assert "fromDate='2025-02-01'" in url
        assert "toDate='2025-02-28'" in url

    def test_get_data_by_external_id_base(self) -> None:
        resource, transport = self._resource()
        resource.get_data(external_id=self._EXT_ID)

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert "getTimeSeriesDataByExternalID?" in url
        assert f"externalID='{self._EXT_ID}'" in url

    def test_get_data_rejects_both_or_neither_identifiers(self) -> None:
        resource, _ = self._resource()
        with pytest.raises(ValueError):
            resource.get_data()
        with pytest.raises(ValueError):
            resource.get_data(time_series_id=self._TS_ID, external_id=self._EXT_ID)

    def test_get_data_rejects_to_date_without_from_date(self) -> None:
        resource, _ = self._resource()
        with pytest.raises(ValueError):
            resource.get_data(time_series_id=self._TS_ID, to_date=date(2025, 2, 28))

    def test_get_history_by_time_series_id(self) -> None:
        resource, transport = self._resource()
        resource.get_history(time_series_id=self._TS_ID)

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert f"{self._PATH_PREFIX}getTimeSeriesDataHistoryByTimeSeriesID?" in url
        assert f"timeSeriesID='{self._TS_ID}'" in url

    def test_get_history_by_external_id_in_period(self) -> None:
        resource, transport = self._resource()
        resource.get_history(
            external_id=self._EXT_ID,
            from_date=date(2025, 2, 1),
            to_date=date(2025, 2, 28),
        )

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert "getTimeSeriesDataHistoryByExternalIDInPeriod?" in url
        assert f"externalID='{self._EXT_ID}'" in url
        assert "fromDate='2025-02-01'" in url
        assert "toDate='2025-02-28'" in url

    def test_paging_params_forwarded(self) -> None:
        resource, transport = self._resource()
        resource.get_data(
            time_series_id=self._TS_ID,
            top=100,
            skip=50,
            order_by="timestamp desc",
        )

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert "$top=100" in url
        assert "$skip=50" in url
        assert "$orderby=timestamp desc" in url

    def test_single_quote_is_escaped_by_doubling(self) -> None:
        resource, transport = self._resource()
        resource.get_data(external_id="a'b")

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        # OData V4 doubles embedded single quotes inside the string literal.
        assert "externalID='a''b'" in url


# ===========================================================================
# TimeSeriesResource - upload
# ===========================================================================


class TestTimeSeriesUpload:
    def test_upload_without_upload_id_hits_uploadsc(self) -> None:
        transport = _make_mock_transport(default_response=_json_response({}))
        http_client = _make_http_client(transport)
        resource = TimeSeriesResource(http_client, BASE_URL)

        resource.upload(BytesIO(b"ts payload"), filename="ts.csv")

        captured = transport._captured_requests  # type: ignore[attr-defined]
        assert captured[0].method == "POST"
        url = _decoded_url(captured[0])
        assert "/api/v1/timeseries/uploadsc" in url
        assert "uploadID" not in url
        # The POST body is multipart form data
        ct = captured[0].headers.get("content-type", "")
        assert ct.startswith("multipart/")

    def test_upload_with_upload_id_hits_upload_with_query(self) -> None:
        transport = _make_mock_transport(default_response=_json_response({}))
        http_client = _make_http_client(transport)
        resource = TimeSeriesResource(http_client, BASE_URL)

        upload_id = UUID("aaaaaaaa-bbbb-cccc-dddd-111122223333")
        resource.upload(b"ts payload", upload_id=upload_id, filename="ts.csv")

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert "/api/v1/timeseries/upload?" in url
        assert f"uploadID={upload_id}" in url
        assert "/uploadsc" not in url


# ===========================================================================
# TimeSeriesResource - delete
# ===========================================================================


class TestTimeSeriesDelete:
    _TS_ID = "123e4567-e89b-12d3-a456-426614174000"

    def test_delete_single_by_uuid(self) -> None:
        transport = _make_mock_transport(
            default_response=httpx.Response(
                status_code=204,
                request=httpx.Request("DELETE", "https://example.com"),
            )
        )
        http_client = _make_http_client(transport)
        resource = TimeSeriesResource(http_client, BASE_URL)

        resource.delete(
            time_series_id=self._TS_ID,
            start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
        )

        captured = transport._captured_requests  # type: ignore[attr-defined]
        assert captured[0].method == "DELETE"
        url = _decoded_url(captured[0])
        assert f"/api/v1/timeseries/delete/{self._TS_ID}" in url
        assert "startTime=" in url
        assert "endTime=" in url

    def test_delete_single_by_external_id(self) -> None:
        transport = _make_mock_transport(
            default_response=httpx.Response(
                status_code=204,
                request=httpx.Request("DELETE", "https://example.com"),
            )
        )
        http_client = _make_http_client(transport)
        resource = TimeSeriesResource(http_client, BASE_URL)

        resource.delete(
            external_id="1+1-1:1.29.0",
            start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
        )

        captured = transport._captured_requests  # type: ignore[attr-defined]
        url = _decoded_url(captured[0])
        assert "/api/v1/timeseries/delete/externalId/1+1-1:1.29.0" in url

    def test_delete_rejects_both_or_neither(self) -> None:
        transport = _make_mock_transport(default_response=_json_response({}))
        http_client = _make_http_client(transport)
        resource = TimeSeriesResource(http_client, BASE_URL)

        with pytest.raises(ValueError):
            resource.delete(
                start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )
        with pytest.raises(ValueError):
            resource.delete(
                time_series_id="a",
                external_id="b",
                start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )

    def test_delete_bulk_posts_body(self) -> None:
        transport = _make_mock_transport(
            default_response=httpx.Response(
                status_code=200,
                json={},
                request=httpx.Request("POST", "https://example.com"),
            )
        )
        http_client = _make_http_client(transport)
        resource = TimeSeriesResource(http_client, BASE_URL)

        req = DeleteTimeSeriesRequest(
            uuids=[UUID(self._TS_ID)],
            external_ids=["1+1-1:1.29.0"],
            start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
        )
        resource.delete_bulk(req)

        captured = transport._captured_requests  # type: ignore[attr-defined]
        assert captured[0].method == "POST"
        url = _decoded_url(captured[0])
        assert "/api/v1/timeseries/delete/bulk" in url

        body = json.loads(captured[0].content)
        assert body["uuids"] == [self._TS_ID]
        assert body["externalIds"] == ["1+1-1:1.29.0"]
        assert "startTime" in body
        assert "endTime" in body


# ===========================================================================
# TimeSeriesResource error propagation
# ===========================================================================


class TestTimeSeriesErrors:
    def test_401(self) -> None:
        transport = _make_mock_transport(default_response=_json_response(_load_json("error_401.json"), 401))
        resource = TimeSeriesResource(_make_http_client(transport), BASE_URL)
        with pytest.raises(MCMAuthenticationError):
            resource.get_data(time_series_id="any")

    def test_403(self) -> None:
        transport = _make_mock_transport(default_response=_json_response(_load_json("error_403.json"), 403))
        resource = TimeSeriesResource(_make_http_client(transport), BASE_URL)
        with pytest.raises(MCMForbiddenError):
            resource.get_data(time_series_id="any")

    def test_404(self) -> None:
        transport = _make_mock_transport(default_response=_json_response(_load_json("error_404.json"), 404))
        resource = TimeSeriesResource(_make_http_client(transport), BASE_URL)
        with pytest.raises(MCMNotFoundError):
            resource.get_data(time_series_id="any")


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
