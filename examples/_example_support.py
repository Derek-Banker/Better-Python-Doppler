from __future__ import annotations

from pathlib import Path
from typing import Any
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from better_python_doppler import Doppler, SecretsClient


class ExampleResponse:
    def __init__(self, *, json_data: Any = None, text: str = "") -> None:
        self._json_data = json_data
        self.text = text

    def json(self) -> Any:
        return self._json_data

    def raise_for_status(self) -> None:
        return None


class ExampleTransport:
    def __init__(self, service_token: str = "dp.st.example-token") -> None:
        self._service_token = service_token
        self.calls: list[dict[str, Any]] = []
        self._responses: list[ExampleResponse] = []

    def queue_json(self, payload: Any) -> None:
        self._responses.append(ExampleResponse(json_data=payload))

    def queue_text(self, text: str) -> None:
        self._responses.append(ExampleResponse(text=text))

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> ExampleResponse:
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

        if not self._responses:
            raise RuntimeError("No example response queued for the requested call.")

        return self._responses.pop(0)

    def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> ExampleResponse:
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
    ) -> ExampleResponse:
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
    ) -> ExampleResponse:
        return self.request(
            "DELETE",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
        )


def build_offline_client(
    service_token: str = "dp.st.example-token",
) -> tuple[Doppler, ExampleTransport]:
    client = Doppler(service_token=service_token)
    transport = ExampleTransport(service_token)
    client._transport = transport
    client._secrets = SecretsClient(service_token, transport=transport)
    return client, transport
