"""Shared helpers for the resource classes.

This module hosts the constants and helper functions used by the
individual resource modules under :mod:`sap_mcm_client._resources`:

* OData base path constants for the MCM, Migration, and Time Series APIs.
* The async HTTP layer (:class:`_AsyncHTTPClient` and :class:`_Response`)
  that wraps :class:`aiohttp.ClientSession`, injects the OAuth2 bearer
  token, and reads the response body eagerly.
* The HTTP-status-to-exception map.
* :func:`_raise_for_status`, which turns failed responses into typed
  :class:`MCMAPIError` instances.
* :func:`_quote_odata_literal`, used by the Time Series resource to wrap
  string query parameters in single quotes.
"""

from __future__ import annotations

import json as _json_module
from typing import Any

import aiohttp

from sap_mcm_client._auth import OAuth2ClientCredentials
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


class _Response:
    """A fully-buffered HTTP response.

    ``aiohttp`` responses can only be read while the underlying connection
    is open, and reading the body is a coroutine. To keep the resource code
    synchronous after the ``await`` on the request, :class:`_AsyncHTTPClient`
    reads the body up-front and hands back this small immutable container.
    """

    def __init__(self, status_code: int, text: str) -> None:
        self.status_code = status_code
        self.text = text

    @property
    def is_success(self) -> bool:
        """Whether the status code is in the 2xx range."""
        return 200 <= self.status_code < 300

    def json(self) -> Any:
        """Parse the body as JSON.

        Raises :class:`json.JSONDecodeError` for a non-JSON body, which
        :func:`_parse_odata_error` catches when classifying error responses.
        """
        return _json_module.loads(self.text)


class _AsyncHTTPClient:
    """Thin async wrapper around :class:`aiohttp.ClientSession`.

    Owns a lazily-created session, injects default OData headers and the
    OAuth2 bearer token on every request, and buffers each response into a
    :class:`_Response` so callers never touch the live ``aiohttp`` response.
    """

    def __init__(
        self,
        *,
        auth: OAuth2ClientCredentials,
        headers: dict[str, str],
        timeout: float,
    ) -> None:
        self._auth = auth
        self._headers = dict(headers)
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        # Created lazily so the session is bound to the running event loop
        # rather than to whatever loop happened to exist at construction.
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self._headers, timeout=self._timeout)
        return self._session

    async def request(
        self,
        method: str,
        url: str,
        *,
        json: Any | None = None,
        params: dict[str, str] | None = None,
        data: aiohttp.FormData | None = None,
    ) -> _Response:
        """Perform an authenticated request and return a buffered response."""
        session = await self._get_session()
        headers = {"Authorization": await self._auth.async_auth_header()}
        async with session.request(
            method,
            url,
            json=json,
            params=params,
            data=data,
            headers=headers,
        ) as response:
            text = await response.text()
            return _Response(response.status, text)

    async def close(self) -> None:
        """Close the underlying session, if one was opened."""
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None


def _parse_odata_error(response: _Response) -> dict[str, Any] | None:
    """Try to extract the OData error body from a failed response."""
    try:
        body = response.json()
        if isinstance(body, dict):
            return body
    except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        pass
    return None


def _raise_for_status(response: _Response) -> None:
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
