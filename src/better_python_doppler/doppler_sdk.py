"""Simple chainable interface for the Doppler API."""
from __future__ import annotations

from typing import Optional
import os

from dotenv import load_dotenv
import requests


class Doppler:
    """Entry point for interacting with Doppler secrets."""

    def __init__(self, service_token: Optional[str] = None, service_token_environ_name: Optional[str] = None) -> None:
        self._token = self._get_service_token(service_token, service_token_environ_name)

    def _get_service_token(self, service_token: Optional[str], service_token_environ_name: Optional[str]) -> str:
        if (service_token is None) == (service_token_environ_name is None):
            raise ValueError(
                "Either `service_token` or `service_token_environ_name` must be provided"
            )
        if service_token is not None:
            return service_token
        load_dotenv()
        pulled_token = os.getenv(service_token_environ_name)  # type: ignore[arg-type]
        if pulled_token is None:
            raise ValueError(
                f"Attempting to retrieve the environmental variable named `{service_token_environ_name}` returned `None`."
            )
        return pulled_token

    def project(self, project_name: str) -> "ProjectHandle":
        """Select a Doppler project."""
        return ProjectHandle(self._token, project_name)


class ProjectHandle:
    """Represents a selected project."""

    def __init__(self, token: str, project_name: str) -> None:
        self._token = token
        self._project_name = project_name

    def config(self, config_name: str) -> "ConfigHandle":
        """Select a config within the current project."""
        return ConfigHandle(self._token, self._project_name, config_name)


class ConfigHandle:
    """Represents a selected config."""

    def __init__(self, token: str, project_name: str, config_name: str) -> None:
        self._token = token
        self._project_name = project_name
        self._config_name = config_name

    def secrets(self) -> "SecretsHandle":
        """Return a handle to work with secrets."""
        return SecretsHandle(self._token, self._project_name, self._config_name)


class SecretsHandle:
    """Operations dealing with secrets."""

    def __init__(self, token: str, project_name: str, config_name: str) -> None:
        self._token = token
        self._project_name = project_name
        self._config_name = config_name

    def get(self, name: str) -> dict:
        """Retrieve a secret value.

        Returns the parsed JSON response from the Doppler API.
        """
        url = (
            f"https://api.doppler.com/v3/configs/config/secret?project={self._project_name}"
            f"&config={self._config_name}&name={name}"
        )
        headers = {"accept": "application/json", "authorization": f"Bearer {self._token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()