from __future__ import annotations

from typing import Any

import pytest

from better_python_doppler import Secrets


class StubResponse:
    def __init__(
        self,
        *,
        json_data: Any = None,
        text: str = "",
        status_error: Exception | None = None,
    ) -> None:
        self._json_data = json_data
        self.text = text
        self._status_error = status_error

    def json(self) -> Any:
        return self._json_data

    def raise_for_status(self) -> None:
        if self._status_error is not None:
            raise self._status_error


class RecordingTransport:
    def __init__(self, service_token: str = "dp.st.test-token") -> None:
        self._service_token = service_token
        self.calls: list[dict[str, Any]] = []
        self.response = StubResponse()

    @property
    def last_call(self) -> dict[str, Any]:
        return self.calls[-1]

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> StubResponse:
        request_headers = dict(headers or {})
        request_headers["Authorization"] = f"Bearer {self._service_token}"
        self.calls.append(
            {
                "method": method.upper(),
                "path": path,
                "params": params,
                "json": json,
                "headers": request_headers,
                "timeout": timeout,
            }
        )
        self.response.raise_for_status()
        return self.response

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> StubResponse:
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
    ) -> StubResponse:
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
    ) -> StubResponse:
        return self.request(
            "DELETE",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
        )


@pytest.fixture
def response_factory():
    def factory(
        *,
        json_data: Any = None,
        text: str = "",
        status_error: Exception | None = None,
    ) -> StubResponse:
        return StubResponse(
            json_data=json_data,
            text=text,
            status_error=status_error,
        )

    return factory


@pytest.fixture
def recording_transport() -> RecordingTransport:
    return RecordingTransport()


@pytest.fixture
def secrets_client(recording_transport: RecordingTransport) -> Secrets:
    return Secrets("dp.st.test-token", transport=recording_transport)
