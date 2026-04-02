from __future__ import annotations

import os
from os import PathLike

from better_python_doppler.exceptions import DopplerConfigError
from better_python_doppler.secret import Secrets, SecretsClient
from better_python_doppler.transport import RequestsTransport


class Doppler:
    def __init__(
        self,
        service_token: str | None = None,
        *,
        service_token_environ_name: str | None = None,
    ) -> None:
        self._service_token = self._get_service_token(
            service_token,
            service_token_environ_name,
        )
        self._transport = RequestsTransport(self._service_token)
        self._project_name: str | None = None
        self._config_name: str | None = None
        self._secrets: SecretsClient | None = None

    @classmethod
    def from_env(
        cls,
        service_token_environ_name: str,
        *,
        dotenv_path: str | PathLike[str] | None = None,
        override: bool = False,
    ) -> "Doppler":
        from dotenv import load_dotenv

        load_kwargs: dict[str, str | PathLike[str] | bool] = {}
        if dotenv_path is not None:
            load_kwargs["dotenv_path"] = dotenv_path
        if override:
            load_kwargs["override"] = True

        load_dotenv(**load_kwargs)
        return cls(service_token_environ_name=service_token_environ_name)

    def _get_service_token(
        self,
        service_token: str | None = None,
        service_token_environ_name: str | None = None,
    ) -> str:
        if (service_token is None) == (service_token_environ_name is None):
            raise DopplerConfigError(
                "Either `service_token` OR `service_token_environ_name` must be provided upon init. NOT both or neither."
            )

        if service_token is not None:
            return service_token

        pulled_token = os.getenv(service_token_environ_name)  # type: ignore[arg-type]

        if pulled_token is None:
            raise DopplerConfigError(
                f"Environment variable `{service_token_environ_name}` is not set."
            )

        return pulled_token

    @property
    def service_token(self) -> str:
        return self._service_token

    def set_scope(self, project_name: str, config_name: str) -> "Doppler":
        self._project_name = project_name
        self._config_name = config_name

        if self._secrets is not None:
            self._secrets.set_scope(project_name, config_name)

        return self

    def clear_scope(self) -> "Doppler":
        self._project_name = None
        self._config_name = None

        if self._secrets is not None:
            self._secrets.clear_scope()

        return self

    @property
    def secrets(self) -> SecretsClient:
        if self._secrets is None:
            self._secrets = SecretsClient(
                self._service_token,
                transport=self._transport,
                project_name=self._project_name,
                config_name=self._config_name,
            )

        return self._secrets

    @property
    def Secrets(self) -> Secrets:
        return self.secrets
