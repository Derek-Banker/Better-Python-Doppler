from __future__ import annotations

from requests import Response


class DopplerError(Exception):
    """Base class for SDK-specific errors."""


class DopplerConfigError(DopplerError, ValueError):
    """Raised when the SDK is configured with invalid local auth inputs."""


class DopplerTransportError(DopplerError):
    """Raised when a request cannot reach the Doppler API successfully."""


class DopplerResponseError(DopplerError):
    """Raised when the Doppler API returns an unexpected response shape."""


class DopplerAPIError(DopplerError):
    """Raised when the Doppler API returns a non-success HTTP response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response: Response | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class DopplerAuthError(DopplerAPIError):
    """Raised for HTTP auth and permission failures from the Doppler API."""


class DopplerNotFoundError(DopplerAPIError):
    """Raised when the Doppler API reports a missing resource."""


class DopplerValidationError(DopplerAPIError):
    """Raised when the Doppler API rejects invalid request inputs."""


__all__ = [
    "DopplerAPIError",
    "DopplerAuthError",
    "DopplerConfigError",
    "DopplerError",
    "DopplerNotFoundError",
    "DopplerResponseError",
    "DopplerTransportError",
    "DopplerValidationError",
]
