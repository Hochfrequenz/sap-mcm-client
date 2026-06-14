"""Tests for the OAuth2ClientCredentials async auth provider."""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import patch

import aiohttp
import pytest
from aioresponses import aioresponses

from sap_mcm_client import MCMAuthError
from sap_mcm_client._auth import OAuth2ClientCredentials

from .conftest import captured_requests

TOKEN_URL = "https://auth.example.com/oauth/token"
CLIENT_ID = "test-client-id"
CLIENT_SECRET = "test-client-secret"


def _token_payload(access_token: str = "tok-123", expires_in: int = 3600) -> dict[str, Any]:
    """Build a mock token endpoint payload."""
    return {"access_token": access_token, "expires_in": expires_in, "token_type": "bearer"}


class TestOAuth2ClientCredentials:
    """Tests for the OAuth2ClientCredentials class."""

    async def test_token_fetched_on_first_request(self) -> None:
        """A bearer token is fetched the first time the header is requested."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with aioresponses() as mocked:
            mocked.post(TOKEN_URL, payload=_token_payload("my-token", 3600))

            header = await auth.async_auth_header()

        assert header == "Bearer my-token"

    async def test_token_is_cached(self) -> None:
        """Subsequent requests reuse the cached token without re-fetching."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with aioresponses() as mocked:
            # Only one token response is registered; a second fetch would
            # raise because no further mock is available.
            mocked.post(TOKEN_URL, payload=_token_payload("cached-token", 3600))

            header1 = await auth.async_auth_header()
            header2 = await auth.async_auth_header()
            requests = captured_requests(mocked)

        assert header1 == "Bearer cached-token"
        assert header2 == "Bearer cached-token"
        # The token endpoint must have been hit exactly once.
        assert len(requests) == 1

    async def test_token_refreshed_when_expired(self) -> None:
        """An expired token triggers a re-fetch."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with aioresponses() as mocked:
            # First token expires in 1s (< 30s margin) so it is already stale.
            mocked.post(TOKEN_URL, payload=_token_payload("token-1", 1))
            mocked.post(TOKEN_URL, payload=_token_payload("token-2", 3600))

            header1 = await auth.async_auth_header()
            assert header1 == "Bearer token-1"

            header2 = await auth.async_auth_header()
            requests = captured_requests(mocked)

        assert header2 == "Bearer token-2"
        assert len(requests) == 2

    async def test_auth_error_on_http_failure(self) -> None:
        """MCMAuthError is raised when the token endpoint returns an error."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with aioresponses() as mocked:
            mocked.post(TOKEN_URL, status=401, payload={"error": "invalid_client"})

            with pytest.raises(MCMAuthError, match="Failed to obtain OAuth2 token"):
                await auth.async_auth_header()

    async def test_auth_error_on_malformed_response(self) -> None:
        """MCMAuthError is raised when the token response is malformed."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with aioresponses() as mocked:
            # Missing access_token key
            mocked.post(TOKEN_URL, payload={"token_type": "bearer"})

            with pytest.raises(MCMAuthError, match="Malformed token response"):
                await auth.async_auth_header()

    async def test_auth_error_on_non_json_response(self) -> None:
        """MCMAuthError is raised when the token endpoint returns a non-JSON body."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with aioresponses() as mocked:
            mocked.post(TOKEN_URL, body="<html>not json</html>", content_type="text/html")

            with pytest.raises(MCMAuthError, match="Malformed token response"):
                await auth.async_auth_header()

    async def test_auth_error_on_connection_failure(self) -> None:
        """MCMAuthError is raised when the token endpoint is unreachable."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with aioresponses() as mocked:
            mocked.post(TOKEN_URL, exception=aiohttp.ClientConnectionError("Connection refused"))

            with pytest.raises(MCMAuthError, match="Failed to obtain OAuth2 token"):
                await auth.async_auth_header()

    async def test_refresh_margin(self) -> None:
        """Token is considered stale 30 seconds before actual expiry."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with aioresponses() as mocked:
            mocked.post(TOKEN_URL, payload=_token_payload("token-1", 31))
            mocked.post(TOKEN_URL, payload=_token_payload("token-2", 3600))

            # First request fetches token-1 (expires in 31s, margin=30, so 1s of validity)
            header1 = await auth.async_auth_header()
            assert header1 == "Bearer token-1"

            # After the expiry window, the next call should refresh. We patch
            # time.monotonic to simulate two seconds passing (beyond validity).
            original_monotonic = time.monotonic
            with patch("sap_mcm_client._auth.time.monotonic") as mock_time:
                mock_time.return_value = original_monotonic() + 2

                header2 = await auth.async_auth_header()

        assert header2 == "Bearer token-2"
