"""Shared fixtures and helpers for SAP MCM client unit tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast
from urllib.parse import unquote, unquote_plus, urlsplit

import httpx
import pytest

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


def _decoded_url(request: httpx.Request) -> str:
    """Return a fully percent-decoded form of the request URL.

    Only the query string is ``unquote_plus``-decoded (``+`` -> space), so
    that literal ``+`` characters in the path (e.g. in an ``externalId``
    segment) survive unchanged for assertions.
    """
    parts = urlsplit(str(request.url))
    path = unquote(parts.path)
    query = unquote_plus(parts.query)
    if query:
        return f"{parts.scheme}://{parts.netloc}{path}?{query}"
    return f"{parts.scheme}://{parts.netloc}{path}"


def _json_response(
    data: dict[str, Any] | list[Any],
    status_code: int = 200,
) -> httpx.Response:
    """Create an httpx.Response with JSON body."""
    return httpx.Response(
        status_code=status_code,
        json=data,
        request=httpx.Request("GET", "https://example.com"),
    )


def _make_mock_transport(
    responses: dict[str, httpx.Response] | None = None,
    default_response: httpx.Response | None = None,
) -> httpx.MockTransport:
    """Create a MockTransport that routes by URL path.

    Parameters
    ----------
    responses:
        Mapping of URL path substrings to responses.
    default_response:
        Fallback response for unmatched URLs.
    """
    captured_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        url_str = str(request.url)
        if responses:
            for path_substr, resp in responses.items():
                if path_substr in url_str:
                    return resp
        if default_response is not None:
            return default_response
        return httpx.Response(status_code=404, request=request)

    transport = httpx.MockTransport(handler)
    transport._captured_requests = captured_requests  # type: ignore[attr-defined]
    return transport


def _make_http_client(transport: httpx.MockTransport) -> httpx.Client:
    """Create an httpx.Client with the given mock transport and no auth."""
    return httpx.Client(transport=transport)


def _make_client_with_transport(transport: httpx.MockTransport) -> tuple[httpx.Client, str]:
    """Create an httpx.Client with the given transport and return (client, base_url)."""
    client = httpx.Client(transport=transport)
    return client, BASE_URL


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
