from __future__ import annotations

import pytest

from better_python_doppler.models import SecretModel


def test_list_parses_secret_models(secrets_client, recording_transport, response_factory) -> None:
    recording_transport.response = response_factory(
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

    result = secrets_client.list("proj", "dev")

    assert [secret.name for secret in result] == ["API_KEY", "TIMEOUT"]
    assert result[0].value.raw == "alpha"
    assert result[0].value.computed == "alpha"
    assert result[0].value.note == "primary"
    assert result[1].value.raw == "30"
    assert recording_transport.last_call["method"] == "GET"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secrets"
    assert recording_transport.last_call["params"] == {
        "project": "proj",
        "config": "dev",
        "include_dynamic_secrets": "true",
        "dynamic_secrets_ttl_sec": 1800,
        "include_managed_secrets": "true",
    }
    assert recording_transport.last_call["headers"] == {
        "Accept": "application/json",
        "Authorization": "Bearer dp.st.test-token",
    }


def test_get_parses_secret_response_into_model(secrets_client, recording_transport, response_factory) -> None:
    recording_transport.response = response_factory(
        json_data={
            "name": "API_KEY",
            "value": {
                "raw": "alpha",
                "computed": "alpha",
                "note": "primary",
            },
        }
    )

    secret = secrets_client.get("proj", "dev", "API_KEY")

    assert isinstance(secret, SecretModel)
    assert secret.name == "API_KEY"
    assert secret.value.raw == "alpha"
    assert secret.value.computed == "alpha"
    assert secret.value.note == "primary"
    assert recording_transport.last_call["method"] == "GET"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secret"
    assert recording_transport.last_call["params"] == {
        "project": "proj",
        "config": "dev",
        "name": "API_KEY",
    }
    assert recording_transport.last_call["headers"] == {
        "accept": "application/json",
        "Authorization": "Bearer dp.st.test-token",
    }


def test_update_requires_secret_input(secrets_client) -> None:
    with pytest.raises(ValueError, match="Invalid Parameter"):
        secrets_client.update("proj", "dev")


def test_update_single_secret_forms_expected_payload(
    secrets_client,
    recording_transport,
    response_factory,
) -> None:
    recording_transport.response = response_factory(
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
    assert recording_transport.last_call["method"] == "POST"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secrets"
    assert recording_transport.last_call["json"] == {
        "project": "proj",
        "config": "dev",
        "secrets": {"API_KEY": "next"},
    }
    assert recording_transport.last_call["headers"] == {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer dp.st.test-token",
    }


def test_update_bulk_secrets_forms_expected_payload(
    secrets_client,
    recording_transport,
    response_factory,
) -> None:
    recording_transport.response = response_factory(
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

    result = secrets_client.update(
        "proj",
        "dev",
        secrets={"API_KEY": "next", "TIMEOUT": "30"},
    )

    assert [secret.name for secret in result] == ["API_KEY", "TIMEOUT"]
    assert recording_transport.last_call["method"] == "POST"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secrets"
    assert recording_transport.last_call["json"] == {
        "project": "proj",
        "config": "dev",
        "secrets": {"API_KEY": "next", "TIMEOUT": "30"},
    }


@pytest.mark.parametrize("format_name", ["json", "dotnet-json"])
def test_download_returns_json_for_json_formats(
    secrets_client,
    recording_transport,
    response_factory,
    format_name: str,
) -> None:
    recording_transport.response = response_factory(json_data={"API_KEY": "alpha"})

    result = secrets_client.download("proj", "dev", format=format_name)

    assert result == {"API_KEY": "alpha"}
    assert recording_transport.last_call["method"] == "GET"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secrets/download"
    assert recording_transport.last_call["params"] == {
        "project": "proj",
        "config": "dev",
        "format": format_name,
        "include_dynamic_secrets": "false",
        "dynamic_secrets_ttl_sec": "1800",
    }
    assert recording_transport.last_call["headers"] == {
        "accept": "application/json",
        "Authorization": "Bearer dp.st.test-token",
    }


@pytest.mark.parametrize("format_name", ["env", "yaml", "docker", "env-no-quotes"])
def test_download_returns_text_for_text_formats(
    secrets_client,
    recording_transport,
    response_factory,
    format_name: str,
) -> None:
    recording_transport.response = response_factory(text="API_KEY=alpha")

    result = secrets_client.download(
        "proj",
        "dev",
        format=format_name,
        name_transformer="lower-snake",
        include_dynamic_secrets=True,
        dynamic_secrets_ttl_sec=60,
        secrets=["API_KEY", "TIMEOUT"],
    )

    assert result == "API_KEY=alpha"
    assert recording_transport.last_call["method"] == "GET"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secrets/download"
    assert recording_transport.last_call["params"] == {
        "project": "proj",
        "config": "dev",
        "format": format_name,
        "include_dynamic_secrets": "true",
        "dynamic_secrets_ttl_sec": "60",
        "name_transformer": "lower-snake",
        "secrets": "API_KEY,TIMEOUT",
    }
    assert recording_transport.last_call["headers"] == {
        "accept": "text/plain",
        "Authorization": "Bearer dp.st.test-token",
    }


def test_delete_calls_delete_endpoint(secrets_client, recording_transport, response_factory) -> None:
    recording_transport.response = response_factory()

    result = secrets_client.delete("proj", "dev", "API_KEY")

    assert result is None
    assert recording_transport.last_call["method"] == "DELETE"
    assert recording_transport.last_call["path"] == "/v3/configs/config/secret"
    assert recording_transport.last_call["params"] == {
        "project": "proj",
        "config": "dev",
        "name": "API_KEY",
    }
    assert recording_transport.last_call["headers"] == {
        "accept": "application/json",
        "Authorization": "Bearer dp.st.test-token",
    }


def test_update_note_posts_expected_payload(
    secrets_client,
    recording_transport,
    response_factory,
) -> None:
    recording_transport.response = response_factory(
        json_data={"secret": "API_KEY", "note": "rotated"}
    )

    result = secrets_client.update_note("proj", "API_KEY", "rotated")

    assert result == {"secret": "API_KEY", "note": "rotated"}
    assert recording_transport.last_call["method"] == "POST"
    assert recording_transport.last_call["path"] == "/v3/projects/project/note"
    assert recording_transport.last_call["params"] == {"project": "proj"}
    assert recording_transport.last_call["json"] == {
        "secret": "API_KEY",
        "note": "rotated",
    }
    assert recording_transport.last_call["headers"] == {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer dp.st.test-token",
    }

