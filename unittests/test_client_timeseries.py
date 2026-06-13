"""Tests for the TimeSeriesResource (read, upload, delete endpoints)."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from io import BytesIO
from typing import Any
from uuid import UUID

import httpx
import pytest

from sap_mcm_client import (
    DeleteTimeSeriesRequest,
    MCMAuthenticationError,
    MCMForbiddenError,
    MCMNotFoundError,
    TimeSeriesDataPoint,
)
from sap_mcm_client._resources import TimeSeriesResource

from .conftest import (
    BASE_URL,
    _decoded_url,
    _json_response,
    _load_json,
    _make_http_client,
    _make_mock_transport,
)

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

    def test_delete_bulk_sends_delete_with_body(self) -> None:
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
        assert captured[0].method == "DELETE"
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
