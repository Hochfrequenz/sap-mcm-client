"""Resource class for the Measurement Concept Class API."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

import httpx

from sap_mcm_client._odata import (
    CLASS_EXPAND_MAP,
    ListResponse,
    build_expand,
    build_query_params,
    parse_collection,
    parse_entity,
)
from sap_mcm_client._resources._base import _BASE_PATH, _raise_for_status
from sap_mcm_client.enums import Division
from sap_mcm_client.types_class import MeasurementConceptClass


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
