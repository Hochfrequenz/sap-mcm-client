"""Shared fixtures and helpers for SAP MCM client unit tests."""

from __future__ import annotations

import contextlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, cast

import pytest
from aioresponses import aioresponses

from sap_mcm_client._auth import OAuth2ClientCredentials
from sap_mcm_client._resources._base import _AsyncHTTPClient, _Response

TESTDATA = Path(__file__).resolve().parent.parent / "testdata"

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

BASE_URL = "https://tenant.example.com"
TOKEN_URL = "https://auth.example.com/oauth/token"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _load_json(name: str) -> dict[str, Any]:
    """Load a JSON fixture from the testdata directory."""
    return cast(dict[str, Any], json.loads((TESTDATA / name).read_text(encoding="utf-8")))


@dataclass
class CapturedRequest:
    """A single request observed by :func:`captured_requests`.

    Mirrors the small surface the tests relied on with the old httpx mock
    transport: the HTTP ``method``, the fully-rendered ``url`` (query string
    included), and the request body (``json`` / ``data``).
    """

    method: str
    url: str
    json: Any = None
    data: Any = None
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def content(self) -> bytes:
        """The JSON body re-encoded as bytes (for ``json.loads`` assertions)."""
        return json.dumps(self.json).encode("utf-8")


def _decoded_url(request: CapturedRequest) -> str:
    """Return the request's URL.

    :func:`captured_requests` already stores a fully-decoded URL (path plus
    the literal query parameter values), so this is a thin accessor kept for
    readability at the call sites.
    """
    return request.url


def _make_response(status_code: int, *, json_body: Any | None = None, text: str = "") -> _Response:
    """Build a buffered :class:`_Response` for direct ``_raise_for_status`` tests."""
    body = json.dumps(json_body) if json_body is not None else text
    return _Response(status_code, body)


def _seeded_auth() -> OAuth2ClientCredentials:
    """An auth object with a pre-seeded token so no token request is made."""
    auth = OAuth2ClientCredentials(TOKEN_URL, "client-id", "client-secret")
    auth._token = "test-token"  # noqa: SLF001  # pylint: disable=protected-access
    auth._expires_at = time.monotonic() + 3600  # noqa: SLF001  # pylint: disable=protected-access
    return auth


def _make_http_client() -> _AsyncHTTPClient:
    """Create an authenticated async HTTP client with a pre-seeded token."""
    return _AsyncHTTPClient(auth=_seeded_auth(), headers={}, timeout=30.0)


def captured_requests(mocked: aioresponses) -> list[CapturedRequest]:
    """Collect every request aioresponses observed, in insertion order.

    The URL is rebuilt from the (decoded) request path and the literal
    ``params`` values the client passed, so assertions can match the
    human-readable query string (e.g. ``$top=10`` or ``externalID='a''b'``)
    without fighting percent-encoding.

    Note: because the query is reconstructed from the ``params`` mapping the
    client supplied, these assertions verify *what the client intended to
    send*, not the exact percent-encoding aiohttp puts on the wire (aiohttp's
    own URL handling is responsible for, and tested for, correct encoding).
    """
    out: list[CapturedRequest] = []
    for (method, url), calls in mocked.requests.items():
        for call in calls:
            base = f"{url.scheme}://{url.host}{url.path}"
            params = call.kwargs.get("params")
            if params:
                query = "&".join(f"{key}={value}" for key, value in params.items())
                full = f"{base}?{query}"
            else:
                full = base
            out.append(
                CapturedRequest(
                    method=method,
                    url=full,
                    json=call.kwargs.get("json"),
                    data=call.kwargs.get("data"),
                    headers=dict(call.kwargs.get("headers") or {}),
                )
            )
    return out


@contextlib.asynccontextmanager
async def mock_client() -> AsyncIterator[tuple[aioresponses, _AsyncHTTPClient]]:
    """Yield an ``(aioresponses, client)`` pair and close the client on exit."""
    with aioresponses() as mocked:
        client = _make_http_client()
        try:
            yield mocked, client
        finally:
            await client.close()


# ---------------------------------------------------------------------------
# JSON fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def instance_get_json() -> dict[str, Any]:
    """Raw JSON for a single instance GET response (with OData envelope)."""
    return _load_json("instance_get.json")


@pytest.fixture()
def instance_list_json() -> dict[str, Any]:
    """Raw JSON for an instance list response."""
    return _load_json("instance_list.json")


@pytest.fixture()
def class_get_json() -> dict[str, Any]:
    """Raw JSON for a single class GET response."""
    return _load_json("class_get.json")


@pytest.fixture()
def class_list_json() -> dict[str, Any]:
    """Raw JSON for a class list response."""
    return _load_json("class_list.json")


@pytest.fixture()
def model_get_json() -> dict[str, Any]:
    """Raw JSON for a single model GET response."""
    return _load_json("model_get.json")


@pytest.fixture()
def model_list_json() -> dict[str, Any]:
    """Raw JSON for a model list response."""
    return _load_json("model_list.json")


@pytest.fixture()
def error_401_json() -> dict[str, Any]:
    """Raw JSON for a 401 error response."""
    return _load_json("error_401.json")


@pytest.fixture()
def error_403_json() -> dict[str, Any]:
    """Raw JSON for a 403 error response."""
    return _load_json("error_403.json")


@pytest.fixture()
def error_404_json() -> dict[str, Any]:
    """Raw JSON for a 404 error response."""
    return _load_json("error_404.json")


@pytest.fixture()
def timeseries_data_json() -> dict[str, Any]:
    """Raw JSON for a Time Series OData read response (v0.2)."""
    return _load_json("timeseries_data.json")


@pytest.fixture()
def migration_response_json() -> dict[str, Any]:
    """Raw JSON for a POST /migrate response (v0.2)."""
    return _load_json("migration_response.json")


@pytest.fixture()
def migration_instance_get_json() -> dict[str, Any]:
    """Raw JSON for a MigrationInstances({id}) GET response (v0.2)."""
    return _load_json("migration_instance_get.json")


@pytest.fixture()
def migration_staged_list_json() -> dict[str, Any]:
    """Raw JSON for a StagedMigrationInstances list response (v0.2)."""
    return _load_json("migration_staged_list.json")
