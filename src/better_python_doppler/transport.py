from __future__ import annotations

from typing import Any, Protocol

import requests
from requests import HTTPError, Response, Session

from better_python_doppler.exceptions import (
    DopplerAPIError,
    DopplerAuthError,
    DopplerNotFoundError,
    DopplerTransportError,
    DopplerValidationError,
)


DEFAULT_BASE_URL = "https://api.doppler.com"
DEFAULT_TIMEOUT_SEC = 10.0


class SyncTransport(Protocol):
    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response: ...

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response: ...

    def post(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response: ...

    def delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response: ...


class RequestsTransport:
    def __init__(
        self,
        service_token: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT_SEC,
        session: Session | None = None,
    ) -> None:
        self._service_token = service_token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = session or requests.Session()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response:
        try:
            response = self._session.request(
                method=method.upper(),
                url=self._build_url(path),
                params=params,
                json=json,
                headers=self._build_headers(headers),
                timeout=self._timeout if timeout is None else timeout,
            )
        except requests.Timeout as exc:
            raise DopplerTransportError("Request to Doppler timed out.") from exc
        except requests.RequestException as exc:
            raise DopplerTransportError(
                "Request to Doppler failed before receiving a response."
            ) from exc

        try:
            response.raise_for_status()
        except HTTPError as exc:
            raise _map_http_error(response) from exc

        return response

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response:
        return self.request(
            "GET",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def post(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response:
        return self.request(
            "POST",
            path,
            params=params,
            json=json,
            headers=headers,
            timeout=timeout,
        )

    def delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> Response:
        return self.request(
            "DELETE",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
        )

    def _build_url(self, path: str) -> str:
        return f"{self._base_url}/{path.lstrip('/')}"

    def _build_headers(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        request_headers = dict(headers or {})
        request_headers["Authorization"] = f"Bearer {self._service_token}"
        return request_headers


def _map_http_error(response: Response) -> DopplerAPIError:
    message = _extract_error_message(response)
    status_code = response.status_code

    if status_code in {401, 403}:
        return DopplerAuthError(
            message,
            status_code=status_code,
            response=response,
        )

    if status_code == 404:
        return DopplerNotFoundError(
            message,
            status_code=status_code,
            response=response,
        )

    if status_code in {400, 422}:
        return DopplerValidationError(
            message,
            status_code=status_code,
            response=response,
        )

    return DopplerAPIError(
        message,
        status_code=status_code,
        response=response,
    )


def _extract_error_message(response: Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        for key in ("message", "error"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        messages = payload.get("messages")
        if isinstance(messages, list):
            parts = [
                part.strip()
                for part in messages
                if isinstance(part, str) and part.strip()
            ]
            if parts:
                return "; ".join(parts)

        errors = payload.get("errors")
        error_message = _flatten_error_details(errors)
        if error_message is not None:
            return error_message

    text = getattr(response, "text", "")
    if isinstance(text, str) and text.strip():
        return text.strip()

    return f"Doppler API request failed with status {response.status_code}."


def _flatten_error_details(errors: Any) -> str | None:
    if isinstance(errors, str) and errors.strip():
        return errors.strip()

    if isinstance(errors, list):
        parts = [part.strip() for part in errors if isinstance(part, str) and part.strip()]
        if parts:
            return "; ".join(parts)
        return None

    if not isinstance(errors, dict):
        return None

    parts: list[str] = []
    for field, details in errors.items():
        prefix = str(field)

        if isinstance(details, str) and details.strip():
            parts.append(f"{prefix}: {details.strip()}")
            continue

        if isinstance(details, list):
            nested_parts = [
                detail.strip()
                for detail in details
                if isinstance(detail, str) and detail.strip()
            ]
            parts.extend(f"{prefix}: {detail}" for detail in nested_parts)

    if parts:
        return "; ".join(parts)

    return None
