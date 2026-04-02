from __future__ import annotations

from typing import Any, Literal

from requests import Response

from better_python_doppler.apis import SecretAPI
from better_python_doppler.exceptions import DopplerResponseError
from better_python_doppler.models import SecretModel, SecretValue
from better_python_doppler.transport import RequestsTransport, SyncTransport


DownloadFormat = Literal[
    "json",
    "dotnet-json",
    "env",
    "yaml",
    "docker",
    "env-no-quotes",
]
NameTransformer = Literal[
    "camel",
    "upper-camel",
    "lower-snake",
    "tf-var",
    "dotnet",
    "dotnet-env",
    "lower-kebab",
]


class SecretsClient:
    def __init__(
        self,
        service_token: str,
        *,
        transport: SyncTransport | None = None,
        project_name: str | None = None,
        config_name: str | None = None,
    ) -> None:
        self._service_token = service_token
        self._transport = transport or RequestsTransport(service_token)
        self._project_name = project_name
        self._config_name = config_name

    def set_scope(self, project_name: str, config_name: str) -> "SecretsClient":
        self._project_name = project_name
        self._config_name = config_name
        return self

    def clear_scope(self) -> "SecretsClient":
        self._project_name = None
        self._config_name = None
        return self

    def list(
        self,
        project_name: str | None = None,
        config_name: str | None = None,
        include_dynamic_secrets: bool = True,
        dynamic_secrets_ttl_sec: int = 1800,
        secrets: list[str] | None = None,
        include_managed_secrets: bool = True,
    ) -> list[SecretModel]:
        project_name, config_name = self._resolve_project_and_config(
            project_name,
            config_name,
            method_name="list",
        )
        response = SecretAPI.list_secrets(
            transport=self._transport,
            project_name=project_name,
            config_name=config_name,
            include_dynamic_secrets=include_dynamic_secrets,
            dynamic_secrets_ttl_sec=dynamic_secrets_ttl_sec,
            secrets=secrets,
            include_managed_secrets=include_managed_secrets,
        )
        return response_to_models(response)

    def list_names(
        self,
        project_name: str | None = None,
        config_name: str | None = None,
        include_dynamic_secrets: bool = False,
        include_managed_secrets: bool = True,
    ) -> list[str]:
        project_name, config_name = self._resolve_project_and_config(
            project_name,
            config_name,
            method_name="list_names",
        )
        response = SecretAPI.list_secret_names(
            transport=self._transport,
            project_name=project_name,
            config_name=config_name,
            include_dynamic_secrets=include_dynamic_secrets,
            include_managed_secrets=include_managed_secrets,
        )
        data = _json_mapping(response, context="secret names")
        names = data.get("names")
        if names is None:
            return []
        if not isinstance(names, list) or not all(
            isinstance(name, str) for name in names
        ):
            raise DopplerResponseError(
                "Doppler secret names response contained an invalid `names` payload."
            )
        return names

    def get(
        self,
        project_name: str | None = None,
        config_name: str | None = None,
        secret_name: str | None = None,
    ) -> SecretModel:
        project_name, config_name, secret_name = (
            self._resolve_project_config_secret_name(
                project_name,
                config_name,
                secret_name,
                method_name="get",
            )
        )
        response = SecretAPI.get_secret(
            transport=self._transport,
            project_name=project_name,
            config_name=config_name,
            secret_name=secret_name,
        )
        return response_to_model(response)

    def get_raw(
        self,
        project_name: str | None = None,
        config_name: str | None = None,
        secret_name: str | None = None,
    ) -> str | None:
        project_name, config_name, secret_name = (
            self._resolve_project_config_secret_name(
                project_name,
                config_name,
                secret_name,
                method_name="get_raw",
            )
        )
        return self.get(project_name, config_name, secret_name).value.raw

    def as_dict(
        self,
        project_name: str | None = None,
        config_name: str | None = None,
        include_dynamic_secrets: bool = True,
        dynamic_secrets_ttl_sec: int = 1800,
        secrets: list[str] | None = None,
        include_managed_secrets: bool = True,
    ) -> dict[str, str | None]:
        project_name, config_name = self._resolve_project_and_config(
            project_name,
            config_name,
            method_name="as_dict",
        )
        return {
            secret.name: secret.value.raw
            for secret in self.list(
                project_name,
                config_name,
                include_dynamic_secrets=include_dynamic_secrets,
                dynamic_secrets_ttl_sec=dynamic_secrets_ttl_sec,
                secrets=secrets,
                include_managed_secrets=include_managed_secrets,
            )
            if secret.name is not None
        }

    def set(
        self,
        project_name: str | None = None,
        config_name: str | None = None,
        secret_name: str | None = None,
        secret_value: str | None = None,
    ) -> SecretModel:
        project_name, config_name, secret_name, secret_value = (
            self._resolve_project_config_secret_value(
                project_name,
                config_name,
                secret_name,
                secret_value,
                method_name="set",
            )
        )
        return self.set_many(
            project_name,
            config_name,
            {secret_name: secret_value},
        )[0]

    def set_many(
        self,
        project_name: str | dict[str, str] | None = None,
        config_name: str | None = None,
        secrets: dict[str, str] | None = None,
    ) -> list[SecretModel]:
        project_name, config_name, secrets = self._resolve_project_config_secrets(
            project_name,
            config_name,
            secrets,
            method_name="set_many",
        )
        response = SecretAPI.update_secrets(
            transport=self._transport,
            project_name=project_name,
            config_name=config_name,
            secrets=secrets,
        )
        return response_to_models(response)

    def update(
        self,
        project_name: str | dict[str, str] | None = None,
        config_name: str | None = None,
        secret_name: str | None = None,
        secret_value: str | None = None,
        *,
        secrets: dict[str, str] | None = None,
    ) -> list[SecretModel]:
        if (
            isinstance(project_name, dict)
            and config_name is None
            and secret_name is None
            and secret_value is None
            and secrets is None
            and self._project_name is not None
            and self._config_name is not None
        ):
            secrets = project_name
            project_name = None

        project_name_input: str | None
        if isinstance(project_name, dict):
            project_name_input = None
        else:
            project_name_input = project_name

        if (
            isinstance(project_name_input, str)
            and isinstance(config_name, str)
            and secret_name is None
            and secret_value is None
            and secrets is None
            and self._project_name is not None
            and self._config_name is not None
        ):
            secret_name = project_name_input
            secret_value = config_name
            project_name_input = None
            config_name = None

        project_name, config_name = self._resolve_project_and_config(
            project_name_input,
            config_name,
            method_name="update",
        )

        if secret_name is not None and secret_value is not None:
            return self.set_many(
                project_name,
                config_name,
                {secret_name: secret_value},
            )

        if secrets is not None:
            return self.set_many(project_name, config_name, secrets)

        raise ValueError(
            "Invalid Parameter: Must provide `secret_name` and `secret_value` or `secrets`."
        )

    def download(
        self,
        project_name: str | None = None,
        config_name: str | None = None,
        format: DownloadFormat = "json",
        name_transformer: NameTransformer | None = None,
        include_dynamic_secrets: bool = False,
        dynamic_secrets_ttl_sec: int = 1800,
        secrets: list[str] | None = None,
    ) -> dict[str, str] | str:
        project_name, config_name = self._resolve_project_and_config(
            project_name,
            config_name,
            method_name="download",
        )
        response = SecretAPI.download_secrets(
            transport=self._transport,
            project_name=project_name,
            config_name=config_name,
            format=format,
            name_transformer=name_transformer,
            include_dynamic_secrets=include_dynamic_secrets,
            dynamic_secrets_ttl_sec=dynamic_secrets_ttl_sec,
            secrets=secrets or [],
        )
        if format in ["json", "dotnet-json"]:
            return _json_mapping(response, context="downloaded secrets")
        return response.text

    def delete(
        self,
        project_name: str | None = None,
        config_name: str | None = None,
        secret_name: str | None = None,
    ) -> None:
        project_name, config_name, secret_name = (
            self._resolve_project_config_secret_name(
                project_name,
                config_name,
                secret_name,
                method_name="delete",
            )
        )
        SecretAPI.delete_secret(
            transport=self._transport,
            project_name=project_name,
            config_name=config_name,
            secret_name=secret_name,
        )

    def update_note(
        self,
        project_name: str | None = None,
        secret_name: str | None = None,
        note: str | None = None,
    ) -> dict[str, object]:
        project_name, secret_name, note = self._resolve_project_secret_note(
            project_name,
            secret_name,
            note,
            method_name="update_note",
        )
        response = SecretAPI.update_note(
            transport=self._transport,
            project_name=project_name,
            secret_name=secret_name,
            note=note,
        )
        return _json_mapping(response, context="secret note update")

    def _resolve_project_and_config(
        self,
        project_name: str | None,
        config_name: str | None,
        *,
        method_name: str,
    ) -> tuple[str, str]:
        resolved_project_name = (
            self._project_name if project_name is None else project_name
        )
        resolved_config_name = (
            self._config_name if config_name is None else config_name
        )

        if resolved_project_name is None or resolved_config_name is None:
            raise TypeError(
                f"{method_name}() requires `project_name` and `config_name` unless a client scope is set."
            )

        return resolved_project_name, resolved_config_name

    def _resolve_project(
        self,
        project_name: str | None,
        *,
        method_name: str,
    ) -> str:
        resolved_project_name = (
            self._project_name if project_name is None else project_name
        )

        if resolved_project_name is None:
            raise TypeError(
                f"{method_name}() requires `project_name` unless a client scope is set."
            )

        return resolved_project_name

    def _resolve_project_config_secret_name(
        self,
        project_name: str | None,
        config_name: str | None,
        secret_name: str | None,
        *,
        method_name: str,
    ) -> tuple[str, str, str]:
        if (
            secret_name is None
            and config_name is None
            and project_name is not None
            and self._project_name is not None
            and self._config_name is not None
        ):
            secret_name = project_name
            project_name = None

        resolved_project_name, resolved_config_name = (
            self._resolve_project_and_config(
                project_name,
                config_name,
                method_name=method_name,
            )
        )

        if secret_name is None:
            raise TypeError(f"{method_name}() requires `secret_name`.")

        return resolved_project_name, resolved_config_name, secret_name

    def _resolve_project_config_secret_value(
        self,
        project_name: str | None,
        config_name: str | None,
        secret_name: str | None,
        secret_value: str | None,
        *,
        method_name: str,
    ) -> tuple[str, str, str, str]:
        if (
            secret_name is None
            and secret_value is None
            and project_name is not None
            and config_name is not None
            and self._project_name is not None
            and self._config_name is not None
        ):
            secret_name = project_name
            secret_value = config_name
            project_name = None
            config_name = None

        resolved_project_name, resolved_config_name = (
            self._resolve_project_and_config(
                project_name,
                config_name,
                method_name=method_name,
            )
        )

        if secret_name is None or secret_value is None:
            raise TypeError(
                f"{method_name}() requires `secret_name` and `secret_value`."
            )

        return (
            resolved_project_name,
            resolved_config_name,
            secret_name,
            secret_value,
        )

    def _resolve_project_config_secrets(
        self,
        project_name: str | dict[str, str] | None,
        config_name: str | None,
        secrets: dict[str, str] | None,
        *,
        method_name: str,
    ) -> tuple[str, str, dict[str, str]]:
        if (
            isinstance(project_name, dict)
            and config_name is None
            and secrets is None
            and self._project_name is not None
            and self._config_name is not None
        ):
            secrets = project_name
            project_name = None

        project_name_input: str | None
        if isinstance(project_name, dict):
            project_name_input = None
        else:
            project_name_input = project_name

        resolved_project_name, resolved_config_name = (
            self._resolve_project_and_config(
                project_name_input,
                config_name,
                method_name=method_name,
            )
        )

        if secrets is None:
            raise TypeError(f"{method_name}() requires `secrets`.")

        return resolved_project_name, resolved_config_name, secrets

    def _resolve_project_secret_note(
        self,
        project_name: str | None,
        secret_name: str | None,
        note: str | None,
        *,
        method_name: str,
    ) -> tuple[str, str, str]:
        if (
            note is None
            and project_name is not None
            and secret_name is not None
            and self._project_name is not None
        ):
            note = secret_name
            secret_name = project_name
            project_name = None

        resolved_project_name = self._resolve_project(
            project_name,
            method_name=method_name,
        )

        if secret_name is None or note is None:
            raise TypeError(
                f"{method_name}() requires `secret_name` and `note`."
            )

        return resolved_project_name, secret_name, note


Secrets = SecretsClient


def response_to_model(response: Response) -> SecretModel:
    data = _json_mapping(response, context="secret")
    name = data.get("name")
    return _secret_from_payload(
        name=name if isinstance(name, str) else None,
        value_payload=data.get("value"),
    )


def response_to_models(response: Response) -> list[SecretModel]:
    data = _json_mapping(response, context="secrets list")
    secrets_payload = data.get("secrets")

    if secrets_payload is None:
        return []

    if not isinstance(secrets_payload, dict):
        raise DopplerResponseError(
            "Doppler secrets list response contained an invalid `secrets` payload."
        )

    return [
        _secret_from_payload(name=name, value_payload=value_payload)
        for name, value_payload in secrets_payload.items()
    ]


def _secret_from_payload(
    name: str | None,
    value_payload: object,
) -> SecretModel:
    value_dict = _secret_value_mapping(value_payload)
    secret_value = SecretValue(
        raw=value_dict.get("raw"),
        computed=value_dict.get("computed"),
        note=value_dict.get("note"),
    )
    return SecretModel(name=name, value=secret_value)


def _json_mapping(response: Response, *, context: str) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError as exc:
        raise DopplerResponseError(
            f"Doppler returned invalid JSON for {context}."
        ) from exc

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise DopplerResponseError(
            f"Doppler returned an unexpected JSON payload for {context}."
        )

    return data


def _secret_value_mapping(value_payload: object) -> dict[str, Any]:
    if value_payload is None:
        return {}

    if not isinstance(value_payload, dict):
        raise DopplerResponseError(
            "Doppler secret response contained an invalid `value` payload."
        )

    return value_payload


__all__ = [
    "Secrets",
    "SecretsClient",
]
