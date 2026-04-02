from __future__ import annotations

from unittest.mock import Mock

import pytest
import requests

from better_python_doppler import Doppler
from better_python_doppler.exceptions import (
    DopplerAPIError,
    DopplerAuthError,
    DopplerConfigError,
    DopplerNotFoundError,
    DopplerResponseError,
    DopplerTransportError,
    DopplerValidationError,
)
from better_python_doppler.models import SecretModel
from better_python_doppler.transport import RequestsTransport


def test_doppler_missing_env_raises_sdk_config_error() -> None:
    with pytest.raises(
        DopplerConfigError,
        match="Environment variable `MISSING_SERVICE_TOKEN` is not set",
    ):
        Doppler(service_token_environ_name="MISSING_SERVICE_TOKEN")


def test_secret_model_default_value_is_not_shared_between_instances() -> None:
    first = SecretModel()
    second = SecretModel()

    first.value.raw = "alpha"

    assert first.value is not second.value
    assert second.value.raw is None


class StubResponse:
    def __init__(self, *, json_data: object = None, text: str = "") -> None:
        self._json_data = json_data
        self.text = text

    def json(self) -> object:
        return self._json_data


class RecordingTransport:
    def __init__(self, response: StubResponse) -> None:
        self._response = response

    def get(
        self,
        path: str,
        *,
        params: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> StubResponse:
        return self._response

    def post(
        self,
        path: str,
        *,
        params: dict[str, object] | None = None,
        json: object = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> StubResponse:
        return self._response

    def delete(
        self,
        path: str,
        *,
        params: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> StubResponse:
        return self._response


def test_secrets_client_treats_null_value_payload_as_empty_secret_value() -> None:
    client = Doppler(service_token="dp.st.test-token")
    client._transport = RecordingTransport(
        StubResponse(json_data={"name": "API_KEY", "value": None})
    )
    client._secrets = None

    secret = client.secrets.get("proj", "dev", "API_KEY")

    assert secret.name == "API_KEY"
    assert secret.value.raw is None
    assert secret.value.computed is None
    assert secret.value.note is None


def test_secrets_client_raises_sdk_error_for_invalid_value_payload() -> None:
    client = Doppler(service_token="dp.st.test-token")
    client._transport = RecordingTransport(
        StubResponse(json_data={"name": "API_KEY", "value": "invalid"})
    )
    client._secrets = None

    with pytest.raises(DopplerResponseError, match="invalid `value` payload"):
        client.secrets.get("proj", "dev", "API_KEY")


def test_secrets_client_treats_null_names_payload_as_empty_list() -> None:
    client = Doppler(service_token="dp.st.test-token")
    client._transport = RecordingTransport(StubResponse(json_data={"names": None}))
    client._secrets = None

    assert client.secrets.list_names("proj", "dev") == []


def test_requests_transport_maps_auth_http_failures_to_sdk_exception() -> None:
    response = Mock()
    response.status_code = 401
    response.text = ""
    response.json.return_value = {"message": "Invalid service token."}
    response.raise_for_status.side_effect = requests.HTTPError(
        "401 Client Error",
        response=response,
    )
    session = Mock()
    session.request.return_value = response

    transport = RequestsTransport("dp.st.test-token", session=session)

    with pytest.raises(DopplerAuthError, match="Invalid service token.") as exc_info:
        transport.get("/v3/configs/config/secrets")

    assert exc_info.value.status_code == 401


def test_requests_transport_maps_not_found_http_failures_to_sdk_exception() -> None:
    response = Mock()
    response.status_code = 404
    response.text = ""
    response.json.return_value = {"messages": ["Secret not found."]}
    response.raise_for_status.side_effect = requests.HTTPError(
        "404 Client Error",
        response=response,
    )
    session = Mock()
    session.request.return_value = response

    transport = RequestsTransport("dp.st.test-token", session=session)

    with pytest.raises(DopplerNotFoundError, match="Secret not found."):
        transport.get("/v3/configs/config/secret")


def test_requests_transport_maps_validation_http_failures_to_sdk_exception() -> None:
    response = Mock()
    response.status_code = 400
    response.text = ""
    response.json.return_value = {"errors": {"config": ["is required"]}}
    response.raise_for_status.side_effect = requests.HTTPError(
        "400 Client Error",
        response=response,
    )
    session = Mock()
    session.request.return_value = response

    transport = RequestsTransport("dp.st.test-token", session=session)

    with pytest.raises(DopplerValidationError, match="config: is required") as exc_info:
        transport.get("/v3/configs/config/secrets")

    assert exc_info.value.status_code == 400


def test_requests_transport_maps_other_http_failures_to_generic_sdk_exception() -> None:
    response = Mock()
    response.status_code = 500
    response.text = "Internal server error."
    response.json.side_effect = ValueError("not json")
    response.raise_for_status.side_effect = requests.HTTPError(
        "500 Server Error",
        response=response,
    )
    session = Mock()
    session.request.return_value = response

    transport = RequestsTransport("dp.st.test-token", session=session)

    with pytest.raises(DopplerAPIError, match="Internal server error.") as exc_info:
        transport.get("/v3/configs/config/secrets")

    assert exc_info.value.status_code == 500


def test_requests_transport_maps_request_failures_to_transport_error() -> None:
    session = Mock()
    session.request.side_effect = requests.ConnectionError("Connection dropped.")

    transport = RequestsTransport("dp.st.test-token", session=session)

    with pytest.raises(
        DopplerTransportError,
        match="Request to Doppler failed before receiving a response.",
    ):
        transport.get("/v3/configs/config/secrets")
