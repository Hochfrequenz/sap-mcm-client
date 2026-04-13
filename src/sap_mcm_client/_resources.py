"""Resource classes that map to the SAP MCM OData V4 API endpoints.

Each resource class encapsulates HTTP interactions for a single entity set
(instances, classes, or models). They are not intended for direct
construction — use :class:`~sap_mcm_client.MCMClient` instead, which
exposes them as ``client.instances``, ``client.classes``, and
``client.models``.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
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
from sap_mcm_client.types_model import MeasurementConceptModel

_BASE_PATH = "/odata/v4/api/mcm/v1"

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
    except Exception:  # noqa: BLE001
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
            f"/MCMInstances({str(instance_id)})/meteringLocations({str(melo_id)})"
            f"/meteringTasks({str(task_id)})",
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
            f"/MCMInstances({str(instance_id)})/meteringLocations({str(melo_id)})"
            "/MCMService.notifyDeviceRemoved",
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
