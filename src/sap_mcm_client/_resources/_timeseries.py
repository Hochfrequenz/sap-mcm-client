"""Resource class for the SAP Cloud for Utilities Foundation Time Series API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, BinaryIO
from uuid import UUID

import httpx

from sap_mcm_client._resources._base import (
    _TIMESERIES_ODATA_BASE_PATH,
    _TIMESERIES_REST_BASE_PATH,
    _quote_odata_literal,
    _raise_for_status,
)
from sap_mcm_client.types_timeseries import DeleteTimeSeriesRequest, TimeSeriesDataPoint


class TimeSeriesResource:
    """Operations on the SAP Cloud for Utilities Foundation Time Series API.

    Covers three groups of endpoints:

    * Twelve OData V4 read functions under ``/odata/v4/api/v1/TimeSeries``
      that return arrays of :class:`TimeSeriesDataPoint`, differentiated by
      identifier type (UUID vs. external ID), current vs. historical data,
      and the optional ``fromDate``/``toDate`` filter.
    * Two REST multipart upload endpoints under ``/api/v1/timeseries``.
    * Three REST delete endpoints, including bulk delete.

    Parameters
    ----------
    client:
        The shared :class:`httpx.Client` configured with authentication.
    base_url:
        The root URL of the Time Series service (same host as MCM).
    """

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    # -- internal helpers ---------------------------------------------------

    def _odata_url(self, path: str) -> str:
        return f"{self._base_url}{_TIMESERIES_ODATA_BASE_PATH}{path}"

    def _rest_url(self, path: str) -> str:
        return f"{self._base_url}{_TIMESERIES_REST_BASE_PATH}{path}"

    def _request(
        self,
        method: str,
        url: str,
        *,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        files: dict[str, Any] | None = None,
    ) -> httpx.Response:
        # ``files`` forces httpx into multipart mode; in that case ``json``
        # must be None to avoid colliding content-type headers.
        response = self._client.request(
            method,
            url,
            json=json,
            params=params,
            files=files,
        )
        _raise_for_status(response)
        return response

    @staticmethod
    def _build_read_params(
        *,
        time_series_id: UUID | str | None,
        external_id: str | None,
        from_date: date | None,
        to_date: date | None,
        top: int | None,
        skip: int | None,
        order_by: str | None,
    ) -> tuple[str, dict[str, str]]:
        """Resolve the endpoint suffix and query string for a read request.

        Picks the base / Since / InPeriod variant based on which of
        ``from_date`` and ``to_date`` are provided, and the ByTimeSeriesID /
        ByExternalID variant based on which identifier is set.

        Returns a tuple of ``(endpoint_suffix, params_dict)``.
        """
        if (time_series_id is None) == (external_id is None):
            raise ValueError("Exactly one of 'time_series_id' or 'external_id' must be provided.")
        if to_date is not None and from_date is None:
            raise ValueError("'to_date' requires 'from_date' to also be set.")

        params: dict[str, str] = {}

        if time_series_id is not None:
            by_suffix = "ByTimeSeriesID"
            params["timeSeriesID"] = _quote_odata_literal(str(time_series_id))
        else:
            by_suffix = "ByExternalID"
            # ``external_id`` is not None by the above check; assert to appease type checkers.
            assert external_id is not None
            params["externalID"] = _quote_odata_literal(external_id)

        if from_date is not None and to_date is not None:
            period_suffix = "InPeriod"
            params["fromDate"] = _quote_odata_literal(from_date.isoformat())
            params["toDate"] = _quote_odata_literal(to_date.isoformat())
        elif from_date is not None:
            period_suffix = "Since"
            params["fromDate"] = _quote_odata_literal(from_date.isoformat())
        else:
            period_suffix = ""

        if top is not None:
            params["$top"] = str(top)
        if skip is not None:
            params["$skip"] = str(skip)
        if order_by is not None:
            params["$orderby"] = order_by

        return by_suffix + period_suffix, params

    def _get_points(self, function_base: str, params: dict[str, str]) -> list[TimeSeriesDataPoint]:
        url = self._odata_url(f"/{function_base}")
        resp = self._request("GET", url, params=params)
        body = resp.json()
        # The OData V4 envelope wraps the array in a ``value`` key.
        raw_items: list[dict[str, Any]]
        if isinstance(body, dict) and "value" in body:
            raw_items = body.get("value") or []
        elif isinstance(body, list):
            raw_items = body
        else:
            raw_items = []
        return [TimeSeriesDataPoint.model_validate(item) for item in raw_items]

    # -- public API ---------------------------------------------------------

    def get_data(
        self,
        *,
        time_series_id: UUID | str | None = None,
        external_id: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        top: int | None = None,
        skip: int | None = None,
        order_by: str | None = None,
    ) -> list[TimeSeriesDataPoint]:
        """Retrieve current time series data points.

        Dispatches to one of six OData read functions based on the
        identifier and date parameters:

        * ``getTimeSeriesDataByTimeSeriesID[Since|InPeriod]``
        * ``getTimeSeriesDataByExternalID[Since|InPeriod]``

        Parameters
        ----------
        time_series_id:
            The UUID of the time series.  Mutually exclusive with
            ``external_id``; exactly one must be given.
        external_id:
            The external identifier of the time series.  Mutually
            exclusive with ``time_series_id``.
        from_date:
            Optional start date (``YYYY-MM-DD``).  When given without
            ``to_date``, the ``Since`` variant is used.
        to_date:
            Optional end date; requires ``from_date``.  When both are
            given, the ``InPeriod`` variant is used.
        top:
            OData ``$top`` — maximum number of points to return.
        skip:
            OData ``$skip`` — number of points to skip.
        order_by:
            OData ``$orderby`` expression.

        Returns
        -------
        list[TimeSeriesDataPoint]
            The matched current data points.
        """
        suffix, params = self._build_read_params(
            time_series_id=time_series_id,
            external_id=external_id,
            from_date=from_date,
            to_date=to_date,
            top=top,
            skip=skip,
            order_by=order_by,
        )
        return self._get_points(f"getTimeSeriesData{suffix}", params)

    def get_history(
        self,
        *,
        time_series_id: UUID | str | None = None,
        external_id: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        top: int | None = None,
        skip: int | None = None,
        order_by: str | None = None,
    ) -> list[TimeSeriesDataPoint]:
        """Retrieve historical time series data points.

        Dispatches to one of six OData read functions based on the
        identifier and date parameters:

        * ``getTimeSeriesDataHistoryByTimeSeriesID[Since|InPeriod]``
        * ``getTimeSeriesDataHistoryByExternalID[Since|InPeriod]``

        See :meth:`get_data` for the parameter semantics.
        """
        suffix, params = self._build_read_params(
            time_series_id=time_series_id,
            external_id=external_id,
            from_date=from_date,
            to_date=to_date,
            top=top,
            skip=skip,
            order_by=order_by,
        )
        return self._get_points(f"getTimeSeriesDataHistory{suffix}", params)

    def upload(
        self,
        file: bytes | BinaryIO,
        *,
        upload_id: UUID | str | None = None,
        filename: str | None = None,
    ) -> None:
        """Upload a time series file.

        If ``upload_id`` is given, the explicit ``/upload`` endpoint is
        used with the UUID in the query string.  Otherwise the
        ``/uploadsc`` endpoint is used, which extracts the time series
        identifier from the file name.

        Parameters
        ----------
        file:
            The file contents (``bytes``) or an open binary stream.
        upload_id:
            Optional explicit upload UUID.  When omitted, the filename-
            based ``/uploadsc`` endpoint is used instead.
        filename:
            Optional filename to send in the multipart body.  Required
            for the filename-based upload endpoint to correctly identify
            the target time series.
        """
        multipart_name = filename if filename is not None else "upload.bin"
        files = {"file": (multipart_name, file)}

        if upload_id is not None:
            url = self._rest_url("/upload")
            params = {"uploadID": str(upload_id)}
            self._request("POST", url, params=params, files=files)
        else:
            url = self._rest_url("/uploadsc")
            self._request("POST", url, files=files)

    def delete(
        self,
        *,
        time_series_id: UUID | str | None = None,
        external_id: str | None = None,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        """Delete time series data by a single identifier within a date range.

        Exactly one of ``time_series_id`` or ``external_id`` must be
        provided.  Both boundaries of the date range are required by the
        API.

        Parameters
        ----------
        time_series_id:
            UUID of the time series to delete from.
        external_id:
            External identifier of the time series to delete from.
        start_time:
            Inclusive start timestamp (UTC).
        end_time:
            Inclusive end timestamp (UTC).
        """
        if (time_series_id is None) == (external_id is None):
            raise ValueError("Exactly one of 'time_series_id' or 'external_id' must be provided.")

        params = {
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat(),
        }

        if time_series_id is not None:
            url = self._rest_url(f"/delete/{str(time_series_id)}")
        else:
            assert external_id is not None
            url = self._rest_url(f"/delete/externalId/{external_id}")

        self._request("DELETE", url, params=params)

    def delete_bulk(self, request: DeleteTimeSeriesRequest) -> None:
        """Delete time series data in bulk by UUID and/or external ID lists.

        The server enforces a maximum of 100 identifiers per request and
        a maximum date range of one year between ``start_time`` and
        ``end_time``.  At least one of ``uuids`` or ``external_ids`` must
        be provided (enforced at request-model construction time).

        Parameters
        ----------
        request:
            The populated :class:`DeleteTimeSeriesRequest` body.
        """
        url = self._rest_url("/delete/bulk")
        payload = request.model_dump(by_alias=True, exclude_none=True, mode="json")
        self._request("DELETE", url, json=payload)
