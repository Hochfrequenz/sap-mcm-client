"""Exception hierarchy for the SAP MCM client.

All API errors inherit from :class:`MCMAPIError`, which carries the HTTP
status code and, when available, the OData error body returned by the server.
Specific subclasses map to well-known HTTP status codes so that callers can
catch exactly the failure mode they care about.
"""

from __future__ import annotations

from typing import Any


class MCMAPIError(Exception):
    """Base exception for all MCM API errors.

    Attributes
    ----------
    status_code:
        The HTTP status code returned by the server.
    detail:
        The parsed OData error body, if the server returned one.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class MCMValidationError(MCMAPIError):
    """Raised when the server rejects a request as invalid (HTTP 400)."""


class MCMAuthenticationError(MCMAPIError):
    """Raised when authentication fails (HTTP 401)."""


class MCMForbiddenError(MCMAPIError):
    """Raised when the server denies access (HTTP 403)."""


class MCMNotFoundError(MCMAPIError):
    """Raised when the requested entity does not exist (HTTP 404)."""
