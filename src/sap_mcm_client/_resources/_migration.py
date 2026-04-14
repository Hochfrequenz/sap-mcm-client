"""Resource class for the Measurement Concept Instance Migration API."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import UUID

import httpx

from sap_mcm_client._odata import (
    MIGRATION_EXPAND_MAP,
    ListResponse,
    build_expand,
    build_query_params,
    parse_collection,
    parse_entity,
)
from sap_mcm_client._resources._base import _MIGRATION_BASE_PATH, _raise_for_status
from sap_mcm_client.types_migration import (
    MigrationInstance,
    MigrationInstanceResponse,
    MigrationResponse,
    StagedMigrationInstance,
)


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
