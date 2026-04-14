"""Shared helpers for the resource classes.

This module hosts the constants and helper functions used by the
individual resource modules under :mod:`sap_mcm_client._resources`:

* OData base path constants for the MCM, Migration, and Time Series APIs.
* The HTTP-status-to-exception map.
* :func:`_raise_for_status`, which turns failed responses into typed
  :class:`MCMAPIError` instances.
* :func:`_quote_odata_literal`, used by the Time Series resource to wrap
  string query parameters in single quotes.
"""

from __future__ import annotations

from typing import Any

import httpx

from sap_mcm_client._errors import (
    MCMAPIError,
    MCMAuthenticationError,
    MCMForbiddenError,
    MCMNotFoundError,
    MCMValidationError,
)

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


def _quote_odata_literal(value: str) -> str:
    """Wrap an OData string literal in single quotes, escaping embedded quotes.

    The Time Series API requires *all* string query parameters (UUIDs,
    external IDs, and ``YYYY-MM-DD`` dates) to be surrounded by single
    quotes per the OData convention.
    """
    escaped = value.replace("'", "''")
    return f"'{escaped}'"
