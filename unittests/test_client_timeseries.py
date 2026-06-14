"""Tests for the TimeSeriesResource (read, upload, delete endpoints)."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from io import BytesIO
from uuid import UUID

import aiohttp
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
    _load_json,
    captured_requests,
    mock_client,
)

_ANY_RE = re.compile(r".*")

# ===========================================================================
# TimeSeriesResource - read endpoints
# ===========================================================================


class TestTimeSeriesReadURLs:
    """Verify that get_data / get_history build the correct OData URL."""

    _TS_ID = "123e4567-e89b-12d3-a456-426614174000"
    _EXT_ID = "1+1-1:1.29.0"
    _PATH_PREFIX = "/odata/v4/api/v1/TimeSeries/"

    async def test_get_data_by_time_series_id_base(self) -> None:
        data = _load_json("timeseries_data.json")
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload=data, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            points = await resource.get_data(time_series_id=self._TS_ID)
            captured = captured_requests(mocked)

        assert len(points) == 4
        assert isinstance(points[0], TimeSeriesDataPoint)

        url = _decoded_url(captured[0])
        assert f"{self._PATH_PREFIX}getTimeSeriesDataByTimeSeriesID?" in url
        # Single-quote literal escaping for the UUID
        assert f"timeSeriesID='{self._TS_ID}'" in url
        assert "fromDate" not in url
        assert "toDate" not in url

    async def test_get_data_by_time_series_id_since(self) -> None:
        data = _load_json("timeseries_data.json")
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload=data, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            await resource.get_data(time_series_id=self._TS_ID, from_date=date(2025, 2, 1))
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert "getTimeSeriesDataByTimeSeriesIDSince?" in url
        assert "fromDate='2025-02-01'" in url
        assert "toDate" not in url

    async def test_get_data_by_time_series_id_in_period(self) -> None:
        data = _load_json("timeseries_data.json")
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload=data, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            await resource.get_data(
                time_series_id=self._TS_ID,
                from_date=date(2025, 2, 1),
                to_date=date(2025, 2, 28),
            )
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert "getTimeSeriesDataByTimeSeriesIDInPeriod?" in url
        assert "fromDate='2025-02-01'" in url
        assert "toDate='2025-02-28'" in url

    async def test_get_data_by_external_id_base(self) -> None:
        data = _load_json("timeseries_data.json")
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload=data, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            await resource.get_data(external_id=self._EXT_ID)
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert "getTimeSeriesDataByExternalID?" in url
        assert f"externalID='{self._EXT_ID}'" in url

    async def test_get_data_rejects_both_or_neither_identifiers(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload={}, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            with pytest.raises(ValueError):
                await resource.get_data()
            with pytest.raises(ValueError):
                await resource.get_data(time_series_id=self._TS_ID, external_id=self._EXT_ID)

    async def test_get_data_rejects_to_date_without_from_date(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload={}, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            with pytest.raises(ValueError):
                await resource.get_data(time_series_id=self._TS_ID, to_date=date(2025, 2, 28))

    async def test_get_history_by_time_series_id(self) -> None:
        data = _load_json("timeseries_data.json")
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload=data, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            await resource.get_history(time_series_id=self._TS_ID)
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert f"{self._PATH_PREFIX}getTimeSeriesDataHistoryByTimeSeriesID?" in url
        assert f"timeSeriesID='{self._TS_ID}'" in url

    async def test_get_history_by_external_id_in_period(self) -> None:
        data = _load_json("timeseries_data.json")
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload=data, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            await resource.get_history(
                external_id=self._EXT_ID,
                from_date=date(2025, 2, 1),
                to_date=date(2025, 2, 28),
            )
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert "getTimeSeriesDataHistoryByExternalIDInPeriod?" in url
        assert f"externalID='{self._EXT_ID}'" in url
        assert "fromDate='2025-02-01'" in url
        assert "toDate='2025-02-28'" in url

    async def test_paging_params_forwarded(self) -> None:
        data = _load_json("timeseries_data.json")
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload=data, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            await resource.get_data(
                time_series_id=self._TS_ID,
                top=100,
                skip=50,
                order_by="timestamp desc",
            )
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert "$top=100" in url
        assert "$skip=50" in url
        assert "$orderby=timestamp desc" in url

    async def test_single_quote_is_escaped_by_doubling(self) -> None:
        data = _load_json("timeseries_data.json")
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload=data, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            await resource.get_data(external_id="a'b")
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        # OData V4 doubles embedded single quotes inside the string literal.
        assert "externalID='a''b'" in url


# ===========================================================================
# TimeSeriesResource - upload
# ===========================================================================


class TestTimeSeriesUpload:
    async def test_upload_without_upload_id_hits_uploadsc(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.post(_ANY_RE, payload={}, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)

            await resource.upload(BytesIO(b"ts payload"), filename="ts.csv")
            captured = captured_requests(mocked)

        assert captured[0].method == "POST"
        url = _decoded_url(captured[0])
        assert "/api/v1/timeseries/uploadsc" in url
        assert "uploadID" not in url
        # The POST body is multipart form data
        assert isinstance(captured[0].data, aiohttp.FormData)

    async def test_upload_with_upload_id_hits_upload_with_query(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.post(_ANY_RE, payload={}, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)

            upload_id = UUID("aaaaaaaa-bbbb-cccc-dddd-111122223333")
            await resource.upload(b"ts payload", upload_id=upload_id, filename="ts.csv")
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert "/api/v1/timeseries/upload?" in url
        assert f"uploadID={upload_id}" in url
        assert "/uploadsc" not in url


# ===========================================================================
# TimeSeriesResource - delete
# ===========================================================================


class TestTimeSeriesDelete:
    _TS_ID = "123e4567-e89b-12d3-a456-426614174000"

    async def test_delete_single_by_uuid(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.delete(_ANY_RE, status=204, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)

            await resource.delete(
                time_series_id=self._TS_ID,
                start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )
            captured = captured_requests(mocked)

        assert captured[0].method == "DELETE"
        url = _decoded_url(captured[0])
        assert f"/api/v1/timeseries/delete/{self._TS_ID}" in url
        assert "startTime=" in url
        assert "endTime=" in url

    async def test_delete_single_by_external_id(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.delete(_ANY_RE, status=204, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)

            await resource.delete(
                external_id="1+1-1:1.29.0",
                start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )
            captured = captured_requests(mocked)

        url = _decoded_url(captured[0])
        assert "/api/v1/timeseries/delete/externalId/1+1-1:1.29.0" in url

    async def test_delete_rejects_both_or_neither(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.delete(_ANY_RE, status=204, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)

            with pytest.raises(ValueError):
                await resource.delete(
                    start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
                )
            with pytest.raises(ValueError):
                await resource.delete(
                    time_series_id="a",
                    external_id="b",
                    start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
                )

    async def test_delete_bulk_sends_delete_with_body(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.delete(_ANY_RE, payload={}, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)

            req = DeleteTimeSeriesRequest(
                uuids=[UUID(self._TS_ID)],
                external_ids=["1+1-1:1.29.0"],
                start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
                end_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
            )
            await resource.delete_bulk(req)
            captured = captured_requests(mocked)

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
    async def test_401(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload=_load_json("error_401.json"), status=401, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            with pytest.raises(MCMAuthenticationError):
                await resource.get_data(time_series_id="any")

    async def test_403(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload=_load_json("error_403.json"), status=403, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            with pytest.raises(MCMForbiddenError):
                await resource.get_data(time_series_id="any")

    async def test_404(self) -> None:
        async with mock_client() as (mocked, client):
            mocked.get(_ANY_RE, payload=_load_json("error_404.json"), status=404, repeat=True)
            resource = TimeSeriesResource(client, BASE_URL)
            with pytest.raises(MCMNotFoundError):
                await resource.get_data(time_series_id="any")
