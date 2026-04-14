"""Tests for the OAuth2ClientCredentials auth handler."""

from __future__ import annotations

import time
from unittest.mock import patch

import httpx
import pytest

from sap_mcm_client import MCMAuthError
from sap_mcm_client._auth import OAuth2ClientCredentials

TOKEN_URL = "https://auth.example.com/oauth/token"
CLIENT_ID = "test-client-id"
CLIENT_SECRET = "test-client-secret"


def _make_token_response(
    access_token: str = "tok-123",
    expires_in: int = 3600,
    status_code: int = 200,
) -> httpx.Response:
    """Create a mock token endpoint response."""
    body = {"access_token": access_token, "expires_in": expires_in, "token_type": "bearer"}
    return httpx.Response(
        status_code=status_code,
        json=body,
        request=httpx.Request("POST", TOKEN_URL),
    )


def _make_token_transport(
    responses: list[httpx.Response] | None = None,
) -> httpx.MockTransport:
    """Create a MockTransport for the token endpoint.

    Each call to the transport pops the next response from the list.
    If no responses are given, a default successful token response is used.
    """
    if responses is None:
        responses = [_make_token_response()]
    call_index = {"i": 0}

    def handler(request: httpx.Request) -> httpx.Response:  # pylint: disable=unused-argument
        idx = call_index["i"]
        call_index["i"] += 1
        if idx < len(responses):
            return responses[idx]
        # Default: keep returning the last response
        return responses[-1]

    return httpx.MockTransport(handler)


class TestOAuth2ClientCredentials:
    """Tests for the OAuth2ClientCredentials class."""

    def test_token_fetched_on_first_request(self) -> None:
        """A bearer token is fetched the first time auth_flow runs."""
        _ = _make_token_transport()

        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        # Simulate the auth_flow by patching the internal httpx.Client usage
        with patch("sap_mcm_client._auth.httpx.Client") as mock_client_cls:
            mock_client = mock_client_cls.return_value.__enter__.return_value
            mock_client.post.return_value = _make_token_response("my-token", 3600)

            request = httpx.Request("GET", "https://api.example.com/data")
            flow = auth.auth_flow(request)
            yielded_request = next(flow)

            assert yielded_request.headers["Authorization"] == "Bearer my-token"

    def test_token_is_cached(self) -> None:
        """Subsequent requests reuse the cached token without re-fetching."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with patch("sap_mcm_client._auth.httpx.Client") as mock_client_cls:
            mock_client = mock_client_cls.return_value.__enter__.return_value
            mock_client.post.return_value = _make_token_response("cached-token", 3600)

            # First request fetches the token
            request1 = httpx.Request("GET", "https://api.example.com/data1")
            flow1 = auth.auth_flow(request1)
            next(flow1)

            # Second request should reuse cached token
            request2 = httpx.Request("GET", "https://api.example.com/data2")
            flow2 = auth.auth_flow(request2)
            yielded = next(flow2)

            assert yielded.headers["Authorization"] == "Bearer cached-token"
            # post should only have been called once
            assert mock_client.post.call_count == 1

    def test_token_refreshed_when_expired(self) -> None:
        """An expired token triggers a re-fetch."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with patch("sap_mcm_client._auth.httpx.Client") as mock_client_cls:
            mock_client = mock_client_cls.return_value.__enter__.return_value
            # First call returns a token that expires very soon
            mock_client.post.side_effect = [
                _make_token_response("token-1", expires_in=1),  # expires in 1s (<30s margin)
                _make_token_response("token-2", expires_in=3600),
            ]

            # First request
            request1 = httpx.Request("GET", "https://api.example.com/data1")
            flow1 = auth.auth_flow(request1)
            r1 = next(flow1)
            assert r1.headers["Authorization"] == "Bearer token-1"

            # The token expires_at = monotonic() + 1 - 30 which is already in the past
            # So the next request should trigger a refresh
            request2 = httpx.Request("GET", "https://api.example.com/data2")
            flow2 = auth.auth_flow(request2)
            r2 = next(flow2)
            assert r2.headers["Authorization"] == "Bearer token-2"
            assert mock_client.post.call_count == 2

    def test_auth_error_on_http_failure(self) -> None:
        """MCMAuthError is raised when the token endpoint returns an error."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with patch("sap_mcm_client._auth.httpx.Client") as mock_client_cls:
            mock_client = mock_client_cls.return_value.__enter__.return_value
            error_resp = httpx.Response(
                status_code=401,
                json={"error": "invalid_client"},
                request=httpx.Request("POST", TOKEN_URL),
            )
            mock_client.post.return_value = error_resp

            request = httpx.Request("GET", "https://api.example.com/data")
            flow = auth.auth_flow(request)

            with pytest.raises(MCMAuthError, match="Failed to obtain OAuth2 token"):
                next(flow)

    def test_auth_error_on_malformed_response(self) -> None:
        """MCMAuthError is raised when the token response is malformed."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with patch("sap_mcm_client._auth.httpx.Client") as mock_client_cls:
            mock_client = mock_client_cls.return_value.__enter__.return_value
            # Missing access_token key
            malformed_resp = httpx.Response(
                status_code=200,
                json={"token_type": "bearer"},
                request=httpx.Request("POST", TOKEN_URL),
            )
            mock_client.post.return_value = malformed_resp

            request = httpx.Request("GET", "https://api.example.com/data")
            flow = auth.auth_flow(request)

            with pytest.raises(MCMAuthError, match="Malformed token response"):
                next(flow)

    def test_auth_error_on_connection_failure(self) -> None:
        """MCMAuthError is raised when the token endpoint is unreachable."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with patch("sap_mcm_client._auth.httpx.Client") as mock_client_cls:
            mock_client = mock_client_cls.return_value.__enter__.return_value
            mock_client.post.side_effect = httpx.ConnectError("Connection refused")

            request = httpx.Request("GET", "https://api.example.com/data")
            flow = auth.auth_flow(request)

            with pytest.raises(MCMAuthError, match="Failed to obtain OAuth2 token"):
                next(flow)

    def test_refresh_margin(self) -> None:
        """Token is considered stale 30 seconds before actual expiry."""
        auth = OAuth2ClientCredentials(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)

        with patch("sap_mcm_client._auth.httpx.Client") as mock_client_cls:
            mock_client = mock_client_cls.return_value.__enter__.return_value
            mock_client.post.side_effect = [
                _make_token_response("token-1", expires_in=31),
                _make_token_response("token-2", expires_in=3600),
            ]

            # First request fetches token-1 (expires in 31s, margin=30, so 1s of validity)
            request1 = httpx.Request("GET", "https://api.example.com/data1")
            flow1 = auth.auth_flow(request1)
            r1 = next(flow1)
            assert r1.headers["Authorization"] == "Bearer token-1"

            # After the expiry window, the next call should refresh
            # We patch time.monotonic to simulate time passing
            original_monotonic = time.monotonic

            with patch("sap_mcm_client._auth.time.monotonic") as mock_time:
                # Simulate 2 seconds have passed (beyond the 1s validity)
                mock_time.return_value = original_monotonic() + 2

                request2 = httpx.Request("GET", "https://api.example.com/data2")
                flow2 = auth.auth_flow(request2)
                r2 = next(flow2)
                assert r2.headers["Authorization"] == "Bearer token-2"
