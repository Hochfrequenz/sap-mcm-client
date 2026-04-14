"""Resource classes that map to the SAP MCM OData V4 API endpoints.

Each resource class encapsulates HTTP interactions for a single entity set
(instances, classes, or models). They are not intended for direct
construction — use :class:`~sap_mcm_client.MCMClient` instead, which
exposes them as ``client.instances``, ``client.classes``, and
``client.models``.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from typing import Any, BinaryIO
from uuid import UUID

import httpx

from sap_mcm_client._errors import (
    MCMAPIError,
    MCMAuthenticationError,
    MCMForbiddenError,
    MCMNotFoundError,
    MCMValidationError,
)
from sap_mcm_client._odata import (
    CLASS_EXPAND_MAP,
    INSTANCE_EXPAND_MAP,
    MIGRATION_EXPAND_MAP,
    MODEL_EXPAND_MAP,
    ListResponse,
    build_expand,
    build_query_params,
    parse_collection,
    parse_entity,
)
from sap_mcm_client.enums import Division, OverallStatus
from sap_mcm_client.types_actions import (
    InitChangeRequest,
    InitMergeRequest,
    InitShutdownRequest,
    InitVersionCancelRequest,
)
from sap_mcm_client.types_class import MeasurementConceptClass
from sap_mcm_client.types_instance import (
    ActorUpdate,
    MarketLocationUpdate,
    MeasurementConceptInstance,
    MeasurementConceptInstanceCreate,
    MeasurementConceptInstanceUpdate,
    MeteringLocationUpdate,
    MeteringTaskUpdate,
    OperandMappingUpdate,
)
from sap_mcm_client.types_migration import (
    MigrationInstance,
    MigrationInstanceResponse,
    MigrationResponse,
    StagedMigrationInstance,
)
from sap_mcm_client.types_model import MeasurementConceptModel
from sap_mcm_client.types_timeseries import DeleteTimeSeriesRequest, TimeSeriesDataPoint

_BASE_PATH = "/odata/v4/api/mcm/v1"
_MIGRATION_BASE_PATH = "/odata/v4/api/migrate/v1"
_TIMESERIES_ODATA_BASE_PATH = "/odata/v4/api/v1/TimeSeries"
_TIMESERIES_REST_BASE_PATH = "/api/v1/timeseries"

# Maps HTTP status codes to specific exception classes.
_STATUS_EXCEPTION_MAP: dict[int, type[MCMAPIError]] = {
    400: MCMValidationError,
    401: MCMAuthenticationError,
    403: MCMForbiddenError,
    404: MCMNotFoundError,
}


def _parse_odata_error(response: httpx.Response) -> dict[str, Any] | None:
    """Try to extract the OData error body from a failed response."""
    try:
        body = response.json()
        if isinstance(body, dict):
            return body
    except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        pass
    return None


def _raise_for_status(response: httpx.Response) -> None:
    """Raise a typed :class:`MCMAPIError` if the response indicates failure."""
    if response.is_success:
        return

    detail = _parse_odata_error(response)

    # Build a human-readable message from the OData error, if present.
    message = f"HTTP {response.status_code}"
    if detail is not None:
        odata_error = detail.get("error", {})
        error_message = odata_error.get("message") if isinstance(odata_error, dict) else None
        if error_message:
            message = f"{message}: {error_message}"
    else:
        message = f"{message}: {response.text[:500]}" if response.text else message

    exc_class = _STATUS_EXCEPTION_MAP.get(response.status_code, MCMAPIError)
    raise exc_class(message, status_code=response.status_code, detail=detail)


# ---------------------------------------------------------------------------
# InstanceResource
# ---------------------------------------------------------------------------


class InstanceResource:
    """Operations on ``MCMInstances`` — the Measurement Concept Instance API.

    Parameters
    ----------
    client:
        The shared :class:`httpx.Client` configured with authentication
        and default OData headers.
    base_url:
        The root URL of the MCM API (e.g.
        ``"https://tenant.example.com"``).  The OData path prefix is
        appended automatically.
    """

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    # -- internal helpers ---------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self._base_url}{_BASE_PATH}{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        response = self._client.request(
            method,
            self._url(path),
            json=json,
            params=params,
        )
        _raise_for_status(response)
        return response

    # -- public API ---------------------------------------------------------

    def list(
        self,
        *,
        include: Sequence[str] | None = None,
        top: int | None = None,
        skip: int | None = None,
        count: bool = False,
        order_by: str | None = None,
        search: str | None = None,
        division: Division | None = None,
        overall_status: OverallStatus | None = None,
        **filters: str | None,
    ) -> ListResponse[MeasurementConceptInstance]:
        """List measurement concept instances.

        Parameters
        ----------
        include:
            Navigation properties to expand.  Valid names are the keys of
            :data:`~sap_mcm_client._odata.INSTANCE_EXPAND_MAP` (e.g.
            ``"metering_locations"``, ``"market_locations"``, ``"all"``).
        top:
            Maximum number of results to return.
        skip:
            Number of results to skip (for pagination).
        count:
            If ``True``, request the total count of matching entities.
        order_by:
            OData ``$orderby`` expression (wire format).
        search:
            Free-text search string.
        division:
            Filter by energy division code.
        overall_status:
            Filter by overall status code.
        **filters:
            Additional OData filter key-value pairs (snake_case field names).

        Returns
        -------
        ListResponse[MeasurementConceptInstance]
            The matched instances and optional count.
        """
        if division is not None:
            filters["division_code"] = str(division)
        if overall_status is not None:
            filters["overall_status_code"] = str(overall_status)

        expand = build_expand(include, INSTANCE_EXPAND_MAP)
        params = build_query_params(
            top=top,
            skip=skip,
            count=count,
            order_by=order_by,
            search=search,
            expand=expand,
            filters=filters if filters else None,
        )

        resp = self._request("GET", "/MCMInstances", params=params)
        return parse_collection(resp.json(), MeasurementConceptInstance)

    def get(
        self,
        instance_id: UUID | str,
        *,
        include: Sequence[str] | None = None,
    ) -> MeasurementConceptInstance:
        """Retrieve a single measurement concept instance by ID.

        Parameters
        ----------
        instance_id:
            The UUID of the instance.
        include:
            Navigation properties to expand.

        Returns
        -------
        MeasurementConceptInstance
            The requested instance.
        """
        expand = build_expand(include, INSTANCE_EXPAND_MAP)
        params = build_query_params(expand=expand)
        resp = self._request(
            "GET",
            f"/MCMInstances({str(instance_id)})",
            params=params,
        )
        return parse_entity(resp.json(), MeasurementConceptInstance)

    def create(
        self,
        data: MeasurementConceptInstanceCreate,
    ) -> MeasurementConceptInstance:
        """Create a new measurement concept instance.

        Parameters
        ----------
        data:
            The creation payload.

        Returns
        -------
        MeasurementConceptInstance
            The newly created instance.
        """
        resp = self._request(
            "POST",
            "/MCMInstances",
            json=data.model_dump(by_alias=True, exclude_none=True),
        )
        return parse_entity(resp.json(), MeasurementConceptInstance)

    def update(
        self,
        instance_id: UUID | str,
        data: MeasurementConceptInstanceUpdate,
    ) -> MeasurementConceptInstance:
        """Update a measurement concept instance.

        Parameters
        ----------
        instance_id:
            The UUID of the instance to update.
        data:
            The update payload.

        Returns
        -------
        MeasurementConceptInstance
            The updated instance.
        """
        resp = self._request(
            "PATCH",
            f"/MCMInstances({str(instance_id)})",
            json=data.model_dump(by_alias=True, exclude_none=True),
        )
        return parse_entity(resp.json(), MeasurementConceptInstance)

    # -- sub-entity updates -------------------------------------------------

    def update_metering_location(
        self,
        instance_id: UUID | str,
        melo_id: UUID | str,
        data: MeteringLocationUpdate,
    ) -> None:
        """Update a metering location of an instance.

        Parameters
        ----------
        instance_id:
            The UUID of the parent instance.
        melo_id:
            The UUID of the metering location.
        data:
            The update payload.
        """
        self._request(
            "PATCH",
            f"/MCMInstances({str(instance_id)})/meteringLocations({str(melo_id)})",
            json=data.model_dump(by_alias=True, exclude_none=True),
        )

    def update_market_location(
        self,
        instance_id: UUID | str,
        malo_id: UUID | str,
        data: MarketLocationUpdate,
    ) -> None:
        """Update a market location of an instance.

        Parameters
        ----------
        instance_id:
            The UUID of the parent instance.
        malo_id:
            The UUID of the market location.
        data:
            The update payload.
        """
        self._request(
            "PATCH",
            f"/MCMInstances({str(instance_id)})/marketLocations({str(malo_id)})",
            json=data.model_dump(by_alias=True, exclude_none=True),
        )

    def update_actor(
        self,
        instance_id: UUID | str,
        actor_id: UUID | str,
        data: ActorUpdate,
    ) -> None:
        """Update an actor of an instance.

        Parameters
        ----------
        instance_id:
            The UUID of the parent instance.
        actor_id:
            The UUID of the actor.
        data:
            The update payload.
        """
        self._request(
            "PATCH",
            f"/MCMInstances({str(instance_id)})/actors({str(actor_id)})",
            json=data.model_dump(by_alias=True, exclude_none=True),
        )

    def update_metering_task(
        self,
        instance_id: UUID | str,
        melo_id: UUID | str,
        task_id: UUID | str,
        data: MeteringTaskUpdate,
    ) -> None:
        """Update a metering task of a metering location.

        Parameters
        ----------
        instance_id:
            The UUID of the parent instance.
        melo_id:
            The UUID of the parent metering location.
        task_id:
            The UUID of the metering task.
        data:
            The update payload.
        """
        self._request(
            "PATCH",
            f"/MCMInstances({str(instance_id)})/meteringLocations({str(melo_id)})" f"/meteringTasks({str(task_id)})",
            json=data.model_dump(by_alias=True, exclude_none=True),
        )

    def update_operand_mapping(
        self,
        instance_id: UUID | str,
        mapping_id: UUID | str,
        data: OperandMappingUpdate,
    ) -> None:
        """Update an operand mapping of an instance.

        Parameters
        ----------
        instance_id:
            The UUID of the parent instance.
        mapping_id:
            The UUID of the operand mapping.
        data:
            The update payload.
        """
        self._request(
            "PATCH",
            f"/MCMInstances({str(instance_id)})/operandMappings({str(mapping_id)})",
            json=data.model_dump(by_alias=True, exclude_none=True),
        )

    # -- lifecycle actions --------------------------------------------------

    def init_change(
        self,
        instance_id: UUID | str,
        data: InitChangeRequest,
    ) -> MeasurementConceptInstance:
        """Initiate a change process for an instance.

        Parameters
        ----------
        instance_id:
            The UUID of the instance.
        data:
            The change request payload.

        Returns
        -------
        MeasurementConceptInstance
            The instance after initiating the change.
        """
        resp = self._request(
            "POST",
            f"/MCMInstances({str(instance_id)})/MCMService.initChange",
            json=data.model_dump(by_alias=True, exclude_none=True),
        )
        return parse_entity(resp.json(), MeasurementConceptInstance)

    def init_merge(
        self,
        instance_id: UUID | str,
        data: InitMergeRequest,
    ) -> MeasurementConceptInstance:
        """Initiate a merge process for an instance.

        Parameters
        ----------
        instance_id:
            The UUID of the instance.
        data:
            The merge request payload.

        Returns
        -------
        MeasurementConceptInstance
            The instance after initiating the merge.
        """
        resp = self._request(
            "POST",
            f"/MCMInstances({str(instance_id)})/MCMService.initMerge",
            json=data.model_dump(by_alias=True, exclude_none=True),
        )
        return parse_entity(resp.json(), MeasurementConceptInstance)

    def init_shutdown(
        self,
        instance_id: UUID | str,
        data: InitShutdownRequest,
    ) -> MeasurementConceptInstance:
        """Initiate a shutdown process for an instance.

        Parameters
        ----------
        instance_id:
            The UUID of the instance.
        data:
            The shutdown request payload.

        Returns
        -------
        MeasurementConceptInstance
            The instance after initiating the shutdown.
        """
        resp = self._request(
            "POST",
            f"/MCMInstances({str(instance_id)})/MCMService.initShutdown",
            json=data.model_dump(by_alias=True, exclude_none=True),
        )
        return parse_entity(resp.json(), MeasurementConceptInstance)

    def init_version_cancel(
        self,
        instance_id: UUID | str,
        data: InitVersionCancelRequest,
    ) -> MeasurementConceptInstance:
        """Cancel a version of an instance.

        Parameters
        ----------
        instance_id:
            The UUID of the instance.
        data:
            The version cancel request payload.

        Returns
        -------
        MeasurementConceptInstance
            The instance after initiating the version cancel.
        """
        resp = self._request(
            "POST",
            f"/MCMInstances({str(instance_id)})/MCMService.initVersionCancel",
            json=data.model_dump(by_alias=True, exclude_none=True),
        )
        return parse_entity(resp.json(), MeasurementConceptInstance)

    def notify_device_removed(
        self,
        instance_id: UUID | str,
        melo_id: UUID | str,
    ) -> None:
        """Notify the API that a device has been removed from a metering location.

        Parameters
        ----------
        instance_id:
            The UUID of the instance.
        melo_id:
            The UUID of the metering location whose device was removed.
        """
        self._request(
            "POST",
            f"/MCMInstances({str(instance_id)})/meteringLocations({str(melo_id)})" "/MCMService.notifyDeviceRemoved",
        )

    def notify_market_location_removed(
        self,
        instance_id: UUID | str,
        malo_id: UUID | str,
    ) -> None:
        """Notify the API that a market location has been removed.

        Parameters
        ----------
        instance_id:
            The UUID of the instance.
        malo_id:
            The UUID of the market location that was removed.
        """
        self._request(
            "POST",
            f"/MCMInstances({str(instance_id)})/marketLocations({str(malo_id)})"
            "/MCMService.notifyMarketLocationRemoved",
        )

    def notify_final_data_entry_ready(
        self,
        instance_id: UUID | str,
        change_process_id: UUID | str,
    ) -> None:
        """Notify the API that the final data entry is ready for a change process.

        Parameters
        ----------
        instance_id:
            The UUID of the instance.
        change_process_id:
            The UUID of the change process.
        """
        self._request(
            "POST",
            f"/MCMInstances({str(instance_id)})/changeProcesses({str(change_process_id)})"
            "/MCMService.notifyFinalDataEntryReady",
        )


# ---------------------------------------------------------------------------
# ClassResource
# ---------------------------------------------------------------------------


class ClassResource:
    """Operations on ``MeasurementConceptClasses`` — the Measurement Concept Class API.

    Parameters
    ----------
    client:
        The shared :class:`httpx.Client`.
    base_url:
        The root URL of the MCM API.
    """

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def _url(self, path: str) -> str:
        return f"{self._base_url}{_BASE_PATH}{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        response = self._client.request(
            method,
            self._url(path),
            params=params,
        )
        _raise_for_status(response)
        return response

    def list(
        self,
        *,
        include: Sequence[str] | None = None,
        top: int | None = None,
        skip: int | None = None,
        count: bool = False,
        division: Division | None = None,
        **filters: str | None,
    ) -> ListResponse[MeasurementConceptClass]:
        """List measurement concept classes.

        Parameters
        ----------
        include:
            Navigation properties to expand.  Valid names are the keys of
            :data:`~sap_mcm_client._odata.CLASS_EXPAND_MAP`.
        top:
            Maximum number of results to return.
        skip:
            Number of results to skip (for pagination).
        count:
            If ``True``, request the total count of matching entities.
        division:
            Filter by energy division code.
        **filters:
            Additional OData filter key-value pairs (snake_case field names).

        Returns
        -------
        ListResponse[MeasurementConceptClass]
            The matched classes and optional count.
        """
        if division is not None:
            filters["division_code"] = str(division)

        expand = build_expand(include, CLASS_EXPAND_MAP)
        params = build_query_params(
            top=top,
            skip=skip,
            count=count,
            expand=expand,
            filters=filters if filters else None,
        )

        resp = self._request("GET", "/MeasurementConceptClasses", params=params)
        return parse_collection(resp.json(), MeasurementConceptClass)

    def get(
        self,
        class_id: UUID | str,
        *,
        include: Sequence[str] | None = None,
    ) -> MeasurementConceptClass:
        """Retrieve a single measurement concept class by ID.

        Parameters
        ----------
        class_id:
            The UUID of the class.
        include:
            Navigation properties to expand.

        Returns
        -------
        MeasurementConceptClass
            The requested class.
        """
        expand = build_expand(include, CLASS_EXPAND_MAP)
        params = build_query_params(expand=expand)
        resp = self._request(
            "GET",
            f"/MeasurementConceptClasses({str(class_id)})",
            params=params,
        )
        return parse_entity(resp.json(), MeasurementConceptClass)


# ---------------------------------------------------------------------------
# ModelResource
# ---------------------------------------------------------------------------


class ModelResource:
    """Operations on ``MeasurementConceptModels`` — the Measurement Concept Model API.

    Parameters
    ----------
    client:
        The shared :class:`httpx.Client`.
    base_url:
        The root URL of the MCM API.
    """

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def _url(self, path: str) -> str:
        return f"{self._base_url}{_BASE_PATH}{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        response = self._client.request(
            method,
            self._url(path),
            params=params,
        )
        _raise_for_status(response)
        return response

    def list(
        self,
        *,
        include: Sequence[str] | None = None,
        top: int | None = None,
        skip: int | None = None,
        count: bool = False,
        division: Division | None = None,
        **filters: str | None,
    ) -> ListResponse[MeasurementConceptModel]:
        """List measurement concept models.

        Parameters
        ----------
        include:
            Navigation properties to expand.  Valid names are the keys of
            :data:`~sap_mcm_client._odata.MODEL_EXPAND_MAP`.
        top:
            Maximum number of results to return.
        skip:
            Number of results to skip (for pagination).
        count:
            If ``True``, request the total count of matching entities.
        division:
            Filter by energy division code.
        **filters:
            Additional OData filter key-value pairs (snake_case field names).

        Returns
        -------
        ListResponse[MeasurementConceptModel]
            The matched models and optional count.
        """
        if division is not None:
            filters["division_code"] = str(division)

        expand = build_expand(include, MODEL_EXPAND_MAP)
        params = build_query_params(
            top=top,
            skip=skip,
            count=count,
            expand=expand,
            filters=filters if filters else None,
        )

        resp = self._request("GET", "/MeasurementConceptModels", params=params)
        return parse_collection(resp.json(), MeasurementConceptModel)

    def get(
        self,
        model_id: UUID | str,
        *,
        include: Sequence[str] | None = None,
    ) -> MeasurementConceptModel:
        """Retrieve a single measurement concept model by ID.

        Parameters
        ----------
        model_id:
            The UUID of the model.
        include:
            Navigation properties to expand.

        Returns
        -------
        MeasurementConceptModel
            The requested model.
        """
        expand = build_expand(include, MODEL_EXPAND_MAP)
        params = build_query_params(expand=expand)
        resp = self._request(
            "GET",
            f"/MeasurementConceptModels({str(model_id)})",
            params=params,
        )
        return parse_entity(resp.json(), MeasurementConceptModel)


# ---------------------------------------------------------------------------
# TimeSeriesResource
# ---------------------------------------------------------------------------


def _quote_odata_literal(value: str) -> str:
    """Wrap an OData string literal in single quotes, escaping embedded quotes.

    The Time Series API requires *all* string query parameters (UUIDs,
    external IDs, and ``YYYY-MM-DD`` dates) to be surrounded by single
    quotes per the OData convention.
    """
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


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
        self._request("POST", url, json=payload)


# ---------------------------------------------------------------------------
# MigrationResource
# ---------------------------------------------------------------------------


class MigrationResource:
    """Operations on the Measurement Concept Instance Migration API.

    The Migration API batch-imports measurement concept instances from legacy
    systems. It lives under a separate OData path
    (``/odata/v4/api/migrate/v1``) but shares authentication with the rest
    of the MCM service.

    Parameters
    ----------
    client:
        The shared :class:`httpx.Client` configured with authentication and
        default OData headers.
    base_url:
        The root URL of the MCM service (e.g. ``"https://tenant.example.com"``).
        The migration path prefix is appended automatically.
    """

    _base_path = _MIGRATION_BASE_PATH

    def __init__(self, client: httpx.Client, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    # -- internal helpers ---------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self._base_url}{self._base_path}{path}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        response = self._client.request(
            method,
            self._url(path),
            json=json,
            params=params,
        )
        _raise_for_status(response)
        return response

    # -- public API ---------------------------------------------------------

    def migrate(self, instances: Sequence[MigrationInstance]) -> MigrationResponse:
        """Submit a batch of measurement concept instances for migration.

        Corresponds to ``POST /odata/v4/api/migrate/v1/migrate``.  The
        endpoint accepts a body of the shape ``{"migrationInstances": [...]}``
        and returns a single request identifier that can be used to query
        the resulting :class:`StagedMigrationInstance` entries.

        Parameters
        ----------
        instances:
            The measurement concept instances to migrate.

        Returns
        -------
        MigrationResponse
            The request identifier of the submitted migration batch.
        """
        payload = {
            "migrationInstances": [
                inst.model_dump(by_alias=True, exclude_none=True, mode="json") for inst in instances
            ],
        }
        resp = self._request("POST", "/migrate", json=payload)
        return parse_entity(resp.json(), MigrationResponse)

    def get(
        self,
        instance_id: UUID | str,
        *,
        include: Sequence[str] | None = None,
    ) -> MigrationInstanceResponse:
        """Retrieve a single migration instance by ID.

        Corresponds to ``GET /odata/v4/api/migrate/v1/MigrationInstances({id})``.

        Parameters
        ----------
        instance_id:
            The UUID of the migration instance.
        include:
            Navigation properties to expand.  Valid names are the keys of
            :data:`~sap_mcm_client._odata.MIGRATION_EXPAND_MAP` (e.g.
            ``"metering_locations"``, ``"market_locations"``, ``"all"``).

        Returns
        -------
        MigrationInstanceResponse
            The requested migration instance.
        """
        expand = build_expand(include, MIGRATION_EXPAND_MAP)
        params = build_query_params(expand=expand)
        resp = self._request(
            "GET",
            f"/MigrationInstances({str(instance_id)})",
            params=params,
        )
        return parse_entity(resp.json(), MigrationInstanceResponse)

    def list_staged(
        self,
        *,
        request_id: UUID | str | None = None,
        status: str | None = None,
        top: int | None = None,
        count: bool = False,
        include_instance: bool = False,
    ) -> ListResponse[StagedMigrationInstance]:
        """List staged migration instances.

        Corresponds to ``GET /odata/v4/api/migrate/v1/StagedMigrationInstances``.
        Supports OData ``$filter``, ``$top``, ``$count``, and ``$expand`` system
        query options.

        Parameters
        ----------
        request_id:
            Optional filter for the migration request UUID returned by
            :meth:`migrate`.
        status:
            Optional filter on the migration status code.
        top:
            Maximum number of staged entries to return.
        count:
            If ``True``, request an inline total count (``$count=true``).
        include_instance:
            If ``True``, expand the ``instance`` navigation property so that
            each :class:`StagedMigrationInstance` carries the full migrated
            measurement concept instance.

        Returns
        -------
        ListResponse[StagedMigrationInstance]
            The matched staged entries and optional count.
        """
        # The StagedMigrationInstances entity uses the plain OData wire
        # name ``requestId`` for its request identifier (not the underscore-
        # separated ``request_id`` that our alias generator would produce).
        # OData V4 Guid literals are unquoted; string literals use single quotes.
        clauses: list[str] = []
        if request_id is not None:
            clauses.append(f"requestId eq {str(request_id)}")
        if status is not None:
            escaped = status.replace("'", "''")
            clauses.append(f"status_code eq '{escaped}'")

        params = build_query_params(
            top=top,
            count=count,
            expand="instance" if include_instance else None,
        )
        if clauses:
            params["$filter"] = " and ".join(clauses)

        resp = self._request("GET", "/StagedMigrationInstances", params=params)
        return parse_collection(resp.json(), StagedMigrationInstance)
