"""High-level client for the SAP MCM OData V4 APIs.

:class:`MCMClient` is the main entry point for interacting with the
Measurement Concept Management service. It manages authentication,
connection pooling, and default headers, and exposes typed resource
accessors for instances, classes, and models.

Usage::

    with MCMClient(
        base_url="https://tenant.example.com",
        token_url="https://auth.example.com/oauth/token",
        client_id="my-client-id",
        client_secret="s3cret",
    ) as client:
        instances = client.instances.list(top=10)
        for inst in instances.items:
            print(inst.id, inst.description)
"""

from __future__ import annotations

from typing import Any

import httpx

from sap_mcm_client._auth import OAuth2ClientCredentials
from sap_mcm_client._odata import ODATA_HEADERS
from sap_mcm_client._resources import ClassResource, InstanceResource, ModelResource


class MCMClient:
    """Typed client for the SAP Cloud for Utilities Foundation MCM APIs.

    Creates an authenticated :class:`httpx.Client` and exposes the three
    MCM API resources as properties.

    Parameters
    ----------
    base_url:
        The root URL of the MCM API (without any path), e.g.
        ``"https://tenant.example.com"``.
    token_url:
        Full URL of the OAuth2 token endpoint.
    client_id:
        The OAuth2 client identifier.
    client_secret:
        The OAuth2 client secret.
    timeout:
        Default request timeout in seconds (applies to connect, read,
        write, and pool).
    """

    def __init__(
        self,
        *,
        base_url: str,
        token_url: str,
        client_id: str,
        client_secret: str,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")

        auth = OAuth2ClientCredentials(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
        )

        self._http = httpx.Client(
            auth=auth,
            headers=ODATA_HEADERS,
            timeout=timeout,
        )

        self._instances = InstanceResource(self._http, self._base_url)
        self._classes = ClassResource(self._http, self._base_url)
        self._models = ModelResource(self._http, self._base_url)

    # -- resource accessors -------------------------------------------------

    @property
    def instances(self) -> InstanceResource:
        """Access the Measurement Concept Instance API."""
        return self._instances

    @property
    def classes(self) -> ClassResource:
        """Access the Measurement Concept Class API."""
        return self._classes

    @property
    def models(self) -> ModelResource:
        """Access the Measurement Concept Model API."""
        return self._models

    # -- lifecycle ----------------------------------------------------------

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> MCMClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
