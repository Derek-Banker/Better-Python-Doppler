from __future__ import annotations

from unittest.mock import patch

import pytest

from better_python_doppler import Doppler, Secrets


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {
            "service_token": "dp.st.direct-token",
            "service_token_environ_name": "SERVICE_TOKEN",
        },
    ],
)
def test_doppler_requires_exactly_one_auth_source(kwargs: dict[str, str]) -> None:
    with pytest.raises(
        ValueError,
        match="Either `service_token` OR `service_token_environ_name`",
    ):
        Doppler(**kwargs)


def test_doppler_uses_direct_service_token() -> None:
    client = Doppler(service_token="dp.st.direct-token")

    assert client.service_token == "dp.st.direct-token"


def test_doppler_loads_token_from_named_env_source_without_loading_dotenv() -> None:
    with (
        patch("dotenv.load_dotenv") as load_dotenv,
        patch("os.getenv", return_value="dp.st.loaded-token") as getenv,
    ):
        client = Doppler(service_token_environ_name="SERVICE_TOKEN")

    assert client.service_token == "dp.st.loaded-token"
    load_dotenv.assert_not_called()
    getenv.assert_called_once_with("SERVICE_TOKEN")


def test_doppler_raises_if_named_env_source_is_missing() -> None:
    with (
        patch("dotenv.load_dotenv") as load_dotenv,
        patch("os.getenv", return_value=None),
    ):
        with pytest.raises(ValueError):
            Doppler(service_token_environ_name="MISSING_SERVICE_TOKEN")

    load_dotenv.assert_not_called()


def test_doppler_from_env_loads_dotenv_before_reading_named_env_source() -> None:
    with (
        patch("dotenv.load_dotenv") as load_dotenv,
        patch("os.getenv", return_value="dp.st.loaded-token") as getenv,
    ):
        client = Doppler.from_env("SERVICE_TOKEN")

    assert client.service_token == "dp.st.loaded-token"
    load_dotenv.assert_called_once_with()
    getenv.assert_called_once_with("SERVICE_TOKEN")


def test_doppler_from_env_accepts_custom_dotenv_path_and_override() -> None:
    with (
        patch("dotenv.load_dotenv") as load_dotenv,
        patch("os.getenv", return_value="dp.st.loaded-token"),
    ):
        client = Doppler.from_env(
            "SERVICE_TOKEN",
            dotenv_path=".env.test",
            override=True,
        )

    assert client.service_token == "dp.st.loaded-token"
    load_dotenv.assert_called_once_with(
        dotenv_path=".env.test",
        override=True,
    )


def test_doppler_secrets_property_remains_cached_compatibility_path() -> None:
    client = Doppler(service_token="dp.st.compat-token")

    first = client.Secrets
    second = client.Secrets

    assert isinstance(first, Secrets)
    assert first is second
    assert first._service_token == "dp.st.compat-token"
