"""Tests for the structured "wide event" logging emitted by the client.

The client follows the canonical-log-line / wide-event approach: exactly
one structured record per outbound request, carrying high-cardinality
context as key-value fields (via ``extra``), with the level reflecting the
outcome. Credentials are never logged.
"""

from __future__ import annotations

import logging
import re

import aiohttp
import pytest
from aioresponses import aioresponses

from sap_mcm_client import MCMAuthError
from sap_mcm_client._auth import OAuth2ClientCredentials
from sap_mcm_client._resources import InstanceResource

from .conftest import (
    BASE_URL,
    _load_json,
    mock_client,
)

_INSTANCES_RE = re.compile(r".*/MCMInstances.*")
_TOKEN_URL = "https://auth.example.com/oauth/token"


def _request_events(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    return [r for r in caplog.records if getattr(r, "event", None) == "mcm.request"]


def _token_events(caplog: pytest.LogCaptureFixture) -> list[logging.LogRecord]:
    return [r for r in caplog.records if getattr(r, "event", None) == "mcm.token_fetch"]


class TestRequestWideEvent:
    """One structured event per outbound API request."""

    async def test_success_emits_single_info_event(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG, logger="sap_mcm_client")
        data = _load_json("instance_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, payload=data, repeat=True)
            resource = InstanceResource(client, BASE_URL)
            await resource.list(top=10)

        events = _request_events(caplog)
        assert len(events) == 1
        record = events[0]
        assert record.levelno == logging.INFO
        assert record.http_method == "GET"  # type: ignore[attr-defined]
        assert record.http_status == 200  # type: ignore[attr-defined]
        assert record.ok is True  # type: ignore[attr-defined]
        assert "MCMInstances" in record.url  # type: ignore[attr-defined]
        assert isinstance(record.duration_ms, float)  # type: ignore[attr-defined]
        assert isinstance(record.request_id, str) and len(record.request_id) == 32  # type: ignore[attr-defined]
        assert record.response_bytes > 0  # type: ignore[attr-defined]

    async def test_request_ids_are_unique_per_request(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG, logger="sap_mcm_client")
        data = _load_json("instance_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, payload=data, repeat=True)
            resource = InstanceResource(client, BASE_URL)
            await resource.list()
            await resource.list()

        events = _request_events(caplog)
        assert len(events) == 2
        assert events[0].request_id != events[1].request_id  # type: ignore[attr-defined]

    async def test_4xx_logged_as_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG, logger="sap_mcm_client")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, payload=_load_json("error_404.json"), status=404, repeat=True)
            resource = InstanceResource(client, BASE_URL)
            with pytest.raises(Exception):  # noqa: B017 — error mapping covered elsewhere
                await resource.get("01234567-89ab-cdef-0123-456789abcdef")

        events = _request_events(caplog)
        assert len(events) == 1
        assert events[0].levelno == logging.WARNING
        assert events[0].http_status == 404  # type: ignore[attr-defined]
        assert events[0].ok is False  # type: ignore[attr-defined]

    async def test_5xx_logged_as_error(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG, logger="sap_mcm_client")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, body="boom", status=503, repeat=True)
            resource = InstanceResource(client, BASE_URL)
            with pytest.raises(Exception):  # noqa: B017
                await resource.list()

        events = _request_events(caplog)
        assert len(events) == 1
        assert events[0].levelno == logging.ERROR
        assert events[0].http_status == 503  # type: ignore[attr-defined]

    async def test_transport_failure_logged_as_error_and_reraised(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG, logger="sap_mcm_client")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, exception=aiohttp.ClientConnectionError("boom"), repeat=True)
            resource = InstanceResource(client, BASE_URL)
            with pytest.raises(aiohttp.ClientError):
                await resource.list()

        events = _request_events(caplog)
        assert len(events) == 1
        assert events[0].levelno == logging.ERROR
        assert events[0].ok is False  # type: ignore[attr-defined]
        assert events[0].error_type == "ClientConnectionError"  # type: ignore[attr-defined]

    async def test_no_credentials_logged(self, caplog: pytest.LogCaptureFixture) -> None:
        """The bearer token, secret, and Authorization header never appear."""
        caplog.set_level(logging.DEBUG, logger="sap_mcm_client")
        data = _load_json("instance_list.json")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, payload=data, repeat=True)
            resource = InstanceResource(client, BASE_URL)
            await resource.list()

        for record in _request_events(caplog):
            blob = f"{record.getMessage()} {record.__dict__}"
            assert "test-token" not in blob
            assert "client-secret" not in blob
            assert "Authorization" not in blob


class TestTokenFetchWideEvent:
    """One structured event per OAuth2 token fetch, with no secrets."""

    async def test_token_fetch_success_event(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG, logger="sap_mcm_client")
        auth = OAuth2ClientCredentials(_TOKEN_URL, "client-id", "super-secret-pw")
        with aioresponses() as mocked:
            mocked.post(_TOKEN_URL, payload={"access_token": "secret-access-token-xyz", "expires_in": 3600})
            await auth.async_auth_header()

        events = _token_events(caplog)
        assert len(events) == 1
        assert events[0].levelno == logging.INFO
        assert events[0].ok is True  # type: ignore[attr-defined]
        assert events[0].expires_in == 3600  # type: ignore[attr-defined]
        # Neither the client secret nor the access token value is logged.
        blob = f"{events[0].getMessage()} {events[0].__dict__}"
        assert "super-secret-pw" not in blob
        assert "secret-access-token-xyz" not in blob

    async def test_token_fetch_failure_event(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG, logger="sap_mcm_client")
        auth = OAuth2ClientCredentials(_TOKEN_URL, "client-id", "super-secret-pw")
        with aioresponses() as mocked:
            mocked.post(_TOKEN_URL, status=401, payload={"error": "invalid_client"})
            with pytest.raises(MCMAuthError):
                await auth.async_auth_header()

        events = _token_events(caplog)
        assert len(events) == 1
        assert events[0].levelno == logging.ERROR
        assert events[0].ok is False  # type: ignore[attr-defined]
        assert "super-secret-pw" not in f"{events[0].getMessage()} {events[0].__dict__}"


class TestLibraryLoggingHygiene:
    """The library must not configure logging for the application."""

    def test_package_logger_has_null_handler(self) -> None:
        pkg_logger = logging.getLogger("sap_mcm_client")
        assert any(isinstance(handler, logging.NullHandler) for handler in pkg_logger.handlers)

    async def test_seeded_auth_does_not_fetch_token(self, caplog: pytest.LogCaptureFixture) -> None:
        """A pre-seeded token must not trigger (or log) a token fetch."""
        caplog.set_level(logging.DEBUG, logger="sap_mcm_client")
        async with mock_client() as (mocked, client):
            mocked.get(_INSTANCES_RE, payload=_load_json("instance_list.json"), repeat=True)
            resource = InstanceResource(client, BASE_URL)
            await resource.list()
        # The seeded token short-circuits _ensure_token: no token fetch happens.
        assert _token_events(caplog) == []
