from __future__ import annotations

from typing import Any

import pytest

from better_python_doppler import Doppler, Secrets, SecretsClient


class StubResponse:
    def __init__(self, *, json_data: Any = None, text: str = "") -> None:
        self._json_data = json_data
        self.text = text

    def json(self) -> Any:
        return self._json_data

    def raise_for_status(self) -> None:
        return None


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
def recording_transport() -> RecordingTransport:
    return RecordingTransport()


@pytest.fixture
def secrets_client(recording_transport: RecordingTransport) -> Secrets:
    return Secrets("dp.st.test-token", transport=recording_transport)


def test_doppler_secrets_properties_share_one_cached_client() -> None:
    client = Doppler(service_token="dp.st.compat-token")

    first = client.secrets
    second = client.secrets
    compatibility = client.Secrets

    assert isinstance(first, SecretsClient)
    assert isinstance(first, Secrets)
    assert first is second
    assert first is compatibility
    assert first._service_token == "dp.st.compat-token"


def test_get_raw_returns_plain_secret_value(
    secrets_client: Secrets,
    recording_transport: RecordingTransport,
) -> None:
    recording_transport.response = StubResponse(
        json_data={
            "name": "API_KEY",
            "value": {
                "raw": "alpha",
                "computed": "alpha",
                "note": "primary",
            },
        }
    )

    result = secrets_client.get_raw("proj", "dev", "API_KEY")

    assert result == "alpha"
    assert recording_transport.last_call["method"] == "GET"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secret"


def test_list_names_returns_secret_names_only(
    secrets_client: Secrets,
    recording_transport: RecordingTransport,
) -> None:
    recording_transport.response = StubResponse(
        json_data={"names": ["API_KEY", "TIMEOUT"]}
    )

    result = secrets_client.list_names("proj", "dev")

    assert result == ["API_KEY", "TIMEOUT"]
    assert recording_transport.last_call["method"] == "GET"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secrets/names"
    assert recording_transport.last_call["params"] == {
        "project": "proj",
        "config": "dev",
        "include_dynamic_secrets": "false",
        "include_managed_secrets": "true",
    }


def test_as_dict_returns_raw_secret_mapping(
    secrets_client: Secrets,
    recording_transport: RecordingTransport,
) -> None:
    recording_transport.response = StubResponse(
        json_data={
            "secrets": {
                "API_KEY": {
                    "raw": "alpha",
                    "computed": "alpha",
                    "note": "primary",
                },
                "TIMEOUT": {
                    "raw": "30",
                    "computed": "30",
                    "note": None,
                },
            }
        }
    )

    result = secrets_client.as_dict("proj", "dev")

    assert result == {"API_KEY": "alpha", "TIMEOUT": "30"}
    assert recording_transport.last_call["method"] == "GET"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secrets"


def test_set_returns_single_secret_model(
    secrets_client: Secrets,
    recording_transport: RecordingTransport,
) -> None:
    recording_transport.response = StubResponse(
        json_data={
            "secrets": {
                "API_KEY": {
                    "raw": "next",
                    "computed": "next",
                    "note": "rotated",
                }
            }
        }
    )

    result = secrets_client.set("proj", "dev", "API_KEY", "next")

    assert result.name == "API_KEY"
    assert result.value.raw == "next"
    assert recording_transport.last_call["method"] == "POST"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secrets"
    assert recording_transport.last_call["json"] == {
        "project": "proj",
        "config": "dev",
        "secrets": {"API_KEY": "next"},
    }


def test_set_many_returns_secret_models(
    secrets_client: Secrets,
    recording_transport: RecordingTransport,
) -> None:
    recording_transport.response = StubResponse(
        json_data={
            "secrets": {
                "API_KEY": {
                    "raw": "next",
                    "computed": "next",
                    "note": None,
                },
                "TIMEOUT": {
                    "raw": "30",
                    "computed": "30",
                    "note": None,
                },
            }
        }
    )

    result = secrets_client.set_many(
        "proj",
        "dev",
        {"API_KEY": "next", "TIMEOUT": "30"},
    )

    assert [secret.name for secret in result] == ["API_KEY", "TIMEOUT"]
    assert recording_transport.last_call["method"] == "POST"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secrets"
    assert recording_transport.last_call["json"] == {
        "project": "proj",
        "config": "dev",
        "secrets": {"API_KEY": "next", "TIMEOUT": "30"},
    }


def test_update_remains_compatibility_wrapper(
    secrets_client: Secrets,
    recording_transport: RecordingTransport,
) -> None:
    recording_transport.response = StubResponse(
        json_data={
            "secrets": {
                "API_KEY": {
                    "raw": "next",
                    "computed": "next",
                    "note": "rotated",
                }
            }
        }
    )

    result = secrets_client.update(
        "proj",
        "dev",
        secret_name="API_KEY",
        secret_value="next",
    )

    assert [secret.name for secret in result] == ["API_KEY"]
    assert result[0].value.raw == "next"
    assert recording_transport.last_call["json"] == {
        "project": "proj",
        "config": "dev",
        "secrets": {"API_KEY": "next"},
    }
