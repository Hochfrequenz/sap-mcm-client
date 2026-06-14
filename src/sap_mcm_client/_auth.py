"""OAuth2 Client Credentials authentication for the SAP MCM APIs.

This module implements the standard OAuth2 Client Credentials flow used by
SAP Cloud Foundry / XSUAA service bindings. It exposes an async token
provider that obtains and caches a bearer token, which the HTTP layer
attaches to every outgoing request.

The token endpoint URL, client ID, and client secret are typically found in
the ``credentials`` block of an SAP BTP service binding (the ``url``,
``clientid``, and ``clientsecret`` fields under the ``uaa`` key).

Concurrency safety: token fetching and caching are guarded by an
:class:`asyncio.Lock`, making this class safe for concurrent use from
multiple coroutines sharing a single :class:`aiohttp.ClientSession`.
"""

from __future__ import annotations

import asyncio
import time

import aiohttp


class MCMAuthError(Exception):
    """Raised when OAuth2 token acquisition fails.

    This can happen when the token endpoint is unreachable, the credentials
    are invalid, or the response does not contain the expected fields.
    """


class OAuth2ClientCredentials:
    """Async auth provider that obtains and caches an OAuth2 bearer token.

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
        self._lock = asyncio.Lock()

    async def async_auth_header(self) -> str:
        """Return the ``Authorization`` header value for an outgoing request.

        If the cached token is missing or about to expire, a fresh token is
        obtained first.
        """
        token = await self._ensure_token()
        return f"Bearer {token}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _ensure_token(self) -> str:
        """Return a valid access token, fetching a new one if necessary."""
        async with self._lock:
            if self._token is not None and time.monotonic() < self._expires_at:
                return self._token
            await self._fetch_token()
            assert self._token is not None  # noqa: S101 — guaranteed by _fetch_token
            return self._token

    async def _fetch_token(self) -> None:
        """POST to the token endpoint and cache the result.

        Raises
        ------
        MCMAuthError
            If the HTTP request fails or the response is malformed.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._token_url,
                    data={"grant_type": "client_credentials"},
                    auth=aiohttp.BasicAuth(self._client_id, self._client_secret),
                ) as response:
                    response.raise_for_status()
                    # ``content_type=None`` disables aiohttp's strict
                    # content-type check so the body is parsed as JSON
                    # regardless of the response's declared content type.
                    payload = await response.json(content_type=None)
        except aiohttp.ClientError as exc:
            raise MCMAuthError(f"Failed to obtain OAuth2 token from {self._token_url}: {exc}") from exc

        try:
            access_token: str = payload["access_token"]
            expires_in: int = int(payload["expires_in"])
        except (KeyError, TypeError, ValueError) as exc:
            raise MCMAuthError(f"Malformed token response from {self._token_url}: {exc}") from exc

        self._token = access_token
        self._expires_at = time.monotonic() + expires_in - self._REFRESH_MARGIN
