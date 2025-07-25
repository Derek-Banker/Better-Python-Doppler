"""Simplified Doppler SDK with a fluent interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import os

from dotenv import load_dotenv

from .handlers import secret as secret_handler


class Doppler:
    """Entry point for interacting with the Doppler API."""

    def __init__(
        self,
        service_token: str | None = None,
        *,
        service_token_environ_name: str | None = None,
    ) -> None:
        self._service_token = self._get_service_token(service_token, service_token_environ_name)

    def _get_service_token(self, direct_token: str | None, env_name: str | None) -> str:
        if (direct_token is None) == (env_name is None):
            raise ValueError(
                "Provide `service_token` or `service_token_environ_name`, not both or neither."
            )

        if direct_token:
            return direct_token

        load_dotenv()
        token = os.getenv(env_name)  # type: ignore[arg-type]
        if token is None:
            raise ValueError(f"Environment variable `{env_name}` is not set")
        return token

    def project(self, project_name: str) -> "ProjectHandle":
        """Select a project by name."""
        return ProjectHandle(self._service_token, project_name)


@dataclass
class ProjectHandle:
    token: str
    project_name: str

    def config(self, config_name: str) -> "ConfigHandle":
        """Select a config within this project."""
        return ConfigHandle(self.token, self.project_name, config_name)


@dataclass
class ConfigHandle:
    token: str
    project_name: str
    config_name: str

    def secrets(self) -> "SecretsHandle":
        """Access secrets for this config."""
        return SecretsHandle(self.token, self.project_name, self.config_name)


@dataclass
class SecretsHandle:
    token: str
    project_name: str
    config_name: str

    def get(self, secret_name: str) -> Any:
        """Retrieve a single secret."""
        resp = secret_handler.get_secret(
            self.token,
            self.project_name,
            self.config_name,
            secret_name,
        )
        resp.raise_for_status()
        return resp.json()

    def list(self) -> Any:
        """List all secrets for the config."""
        resp = secret_handler.list_secrets(
            self.token,
            self.project_name,
            self.config_name,
        )
        resp.raise_for_status()
        return resp.json()

