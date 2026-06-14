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
import logging
import time
from typing import Any
from uuid import uuid4

import aiohttp

from sap_mcm_client._auth import OAuth2ClientCredentials
from sap_mcm_client._errors import (
    MCMAPIError,
    MCMAuthenticationError,
    MCMForbiddenError,
    MCMNotFoundError,
    MCMValidationError,
)

#: Logger for the one structured "wide event" emitted per outbound request.
#: A child of the ``sap_mcm_client`` package logger, so configuring that
#: logger (or a parent) controls this output. See the README Logging section.
logger = logging.getLogger(__name__)

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
        # ``Content-Type`` is applied per-request rather than as a session
        # default: aiohttp sets the correct content type automatically for
        # each body kind (``application/json`` for ``json=``, multipart with a
        # boundary for ``FormData``). A session-wide ``Content-Type`` would
        # clobber the multipart type on uploads. We still want the OData JSON
        # content type (with ``IEEE754Compatible=true``) on JSON bodies, so we
        # keep it aside and attach it only when a JSON body is sent.
        request_headers = dict(headers)
        self._json_content_type = request_headers.pop("Content-Type", None)
        self._headers = request_headers
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
        """Perform an authenticated request and return a buffered response.

        Emits exactly one structured log record ("wide event") per request on
        the ``sap_mcm_client`` logger: a single canonical line carrying the
        method, URL, status, duration, and a high-cardinality ``request_id``,
        rather than several fragmented messages. Credentials (the bearer
        token, request headers) are never logged.
        """
        session = await self._get_session()
        headers = {"Authorization": await self._auth.async_auth_header()}
        # Only attach the OData JSON content type when sending a JSON body;
        # uploads pass ``data`` (FormData) and must keep aiohttp's multipart
        # content type with its boundary.
        if json is not None and self._json_content_type is not None:
            headers["Content-Type"] = self._json_content_type

        request_id = uuid4().hex
        started = time.monotonic()
        try:
            async with session.request(
                method,
                url,
                json=json,
                params=params,
                data=data,
                headers=headers,
            ) as response:
                text = await response.text()
        except Exception as exc:
            # Transport-level failure (no HTTP response). Always recorded.
            self._log_event(method, url, request_id, started, error=exc)
            raise

        self._log_event(method, url, request_id, started, status=response.status, text=text)
        return _Response(response.status, text)

    @staticmethod
    def _log_event(
        method: str,
        url: str,
        request_id: str,
        started: float,
        *,
        status: int | None = None,
        text: str | None = None,
        error: Exception | None = None,
    ) -> None:
        """Emit the single structured "wide event" for one request.

        ``status``/``text`` describe a completed response; ``error`` marks a
        transport-level failure. The level reflects the outcome so errors
        always surface even when the happy path is quiet: 2xx -> INFO,
        4xx -> WARNING, 5xx and transport errors -> ERROR.
        """
        duration_ms = round((time.monotonic() - started) * 1000, 3)
        extra: dict[str, Any] = {
            "event": "mcm.request",
            "request_id": request_id,
            "http_method": method,
            "url": url,
            "duration_ms": duration_ms,
        }
        if error is not None:
            extra.update(ok=False, error_type=type(error).__name__, error=str(error))
            logger.error("mcm request failed: %s %s (%s)", method, url, type(error).__name__, extra=extra)
            return

        assert status is not None  # noqa: S101 — provided on the success path
        extra.update(http_status=status, response_bytes=len(text or ""), ok=200 <= status < 300)
        level = logging.ERROR if status >= 500 else logging.WARNING if status >= 400 else logging.INFO
        logger.log(level, "mcm request: %s %s -> %d in %.1fms", method, url, status, duration_ms, extra=extra)

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
