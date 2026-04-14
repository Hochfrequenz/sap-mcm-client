"""OAuth2 Client Credentials authentication for the SAP MCM APIs.

This module implements the standard OAuth2 Client Credentials flow used by
SAP Cloud Foundry / XSUAA service bindings. It plugs into ``httpx``'s auth
protocol so that token acquisition and refresh happen transparently.

The token endpoint URL, client ID, and client secret are typically found in
the ``credentials`` block of an SAP BTP service binding (the ``url``,
``clientid``, and ``clientsecret`` fields under the ``uaa`` key).

Thread safety: token fetching and caching are guarded by a
:class:`threading.Lock`, making this class safe for use with
:class:`httpx.Client` from multiple threads.
"""

from __future__ import annotations

import threading
import time
from typing import Generator

import httpx


class MCMAuthError(Exception):
    """Raised when OAuth2 token acquisition fails.

    This can happen when the token endpoint is unreachable, the credentials
    are invalid, or the response does not contain the expected fields.
    """


class OAuth2ClientCredentials(httpx.Auth):
    """httpx-compatible auth that obtains and caches an OAuth2 bearer token.

    Uses the *Client Credentials* grant type: a POST to the token endpoint
    with HTTP Basic authentication (``client_id:client_secret``) and
    ``grant_type=client_credentials``.

    The token is cached and reused until 30 seconds before its expiry
    (based on :func:`time.monotonic`), at which point a fresh token is
    requested automatically.

    Parameters
    ----------
    token_url:
        Full URL of the OAuth2 token endpoint, e.g.
        ``"https://<subdomain>.authentication.eu10.hana.ondemand.com/oauth/token"``.
    client_id:
        The OAuth2 client identifier.
    client_secret:
        The OAuth2 client secret.
    """

    #: Number of seconds before actual expiry at which the token is
    #: considered stale and a new one is fetched.
    _REFRESH_MARGIN: float = 30.0

    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret

        self._token: str | None = None
        self._expires_at: float = 0.0
        self._lock = threading.Lock()

    def auth_flow(
        self,
        request: httpx.Request,
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Attach a valid bearer token to every outgoing request.

        If the cached token is missing or about to expire, a fresh token is
        obtained first. This method conforms to the ``httpx.Auth`` protocol.
        """
        token = self._ensure_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_token(self) -> str:
        """Return a valid access token, fetching a new one if necessary."""
        with self._lock:
            if self._token is not None and time.monotonic() < self._expires_at:
                return self._token
            self._fetch_token()
            assert self._token is not None  # noqa: S101 — guaranteed by _fetch_token
            return self._token

    def _fetch_token(self) -> None:
        """POST to the token endpoint and cache the result.

        Raises
        ------
        MCMAuthError
            If the HTTP request fails or the response is malformed.
        """
        try:
            with httpx.Client() as client:
                response = client.post(
                    self._token_url,
                    data={"grant_type": "client_credentials"},
                    auth=(self._client_id, self._client_secret),
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise MCMAuthError(f"Failed to obtain OAuth2 token from {self._token_url}: {exc}") from exc

        try:
            payload = response.json()
            access_token: str = payload["access_token"]
            expires_in: int = int(payload["expires_in"])
        except (KeyError, TypeError, ValueError) as exc:
            raise MCMAuthError(f"Malformed token response from {self._token_url}: {exc}") from exc

        self._token = access_token
        self._expires_at = time.monotonic() + expires_in - self._REFRESH_MARGIN
