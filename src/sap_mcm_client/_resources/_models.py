"""Resource class for the Measurement Concept Model API."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sap_mcm_client._odata import (
    MODEL_EXPAND_MAP,
    ListResponse,
    build_expand,
    build_query_params,
    parse_collection,
    parse_entity,
)
from sap_mcm_client._resources._base import _BASE_PATH, _AsyncHTTPClient, _raise_for_status, _Response
from sap_mcm_client.enums import Division
from sap_mcm_client.types_model import MeasurementConceptModel


class ModelResource:
    """Operations on ``MeasurementConceptModels`` — the Measurement Concept Model API.

    Parameters
    ----------
    client:
        The shared authenticated async HTTP client.
    base_url:
        The root URL of the MCM API.
    """

    def __init__(self, client: _AsyncHTTPClient, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    def _url(self, path: str) -> str:
        return f"{self._base_url}{_BASE_PATH}{path}"

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> _Response:
        response = await self._client.request(
            method,
            self._url(path),
            params=params,
        )
        _raise_for_status(response)
        return response

    async def list(
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

        resp = await self._request("GET", "/MeasurementConceptModels", params=params)
        return parse_collection(resp.json(), MeasurementConceptModel)

    async def get(
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
        resp = await self._request(
            "GET",
            f"/MeasurementConceptModels({str(model_id)})",
            params=params,
        )
        return parse_entity(resp.json(), MeasurementConceptModel)
