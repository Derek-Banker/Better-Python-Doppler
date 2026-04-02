# Better Python Doppler

Better Python Doppler is a lightweight, sync, secrets-first Python SDK for the [Doppler API](https://docs.doppler.com/reference).

The supported public surface today is secrets management. This repo is not yet documenting or claiming first-class public support for projects, configs, or environments.

Related repo docs:

- [Project Outline](PROJECT_OUTLINE.md)
- [Development Plan](DEVELOPMENT_PLAN.md)

## Installation

This project currently requires Python 3.12 or newer.

The package name is `better-python-doppler`.

```bash
pip install better-python-doppler
```

Runtime dependencies are declared in `pyproject.toml`, including `requests` and `python-dotenv`.

For a source checkout, the verified local install path is:

```bash
pip install -e .[test]
```

## Current Scope

Supported and documented today:

- direct token auth with `Doppler(service_token="...")`
- explicit environment lookup with `Doppler(service_token_environ_name="...")`
- explicit `.env` loading with `Doppler.from_env(...)`
- secrets access through `client.secrets`
- compatibility access through `client.Secrets`
- top-level compatibility exports: `Secrets` and `SecretsClient`
- SDK exception types exported from `better_python_doppler`

Supported secrets workflows:

- `list`
- `list_names`
- `get`
- `get_raw`
- `as_dict`
- `set`
- `set_many`
- `update` as a compatibility wrapper
- `delete`
- `update_note`
- `download`

Not documented as supported public SDK surface yet:

- projects client
- configs client
- environments client

## Authentication

### Direct Token

```python
from better_python_doppler import Doppler

client = Doppler(service_token="dp.st.example-token")
```

### Explicit Environment Lookup

```python
from better_python_doppler import Doppler

client = Doppler(service_token_environ_name="DOPPLER_SERVICE_TOKEN")
```

This reads the named environment variable directly. It does not implicitly load `.env`.

### Explicit `.env` Workflow

```python
from better_python_doppler import Doppler

client = Doppler.from_env(
    "DOPPLER_SERVICE_TOKEN",
    dotenv_path=".env",
    override=False,
)
```

Use `from_env(...)` when you want `.env` loading to be explicit instead of hidden in the base constructor.

## Secrets Usage

Recommended usage goes through `client.secrets`.

```python
from better_python_doppler import Doppler

client = Doppler(service_token="dp.st.example-token")

secret = client.secrets.get("my-project", "dev", "API_KEY")
print(secret.name)
print(secret.value.raw)

raw_value = client.secrets.get_raw("my-project", "dev", "API_KEY")
print(raw_value)
```

### Single Secret Set/Get

```python
updated = client.secrets.set(
    "my-project",
    "dev",
    "API_KEY",
    "next-value",
)

print(updated.value.raw)
print(client.secrets.get_raw("my-project", "dev", "API_KEY"))
```

### Multi-Secret Set/Update

```python
updated = client.secrets.set_many(
    "my-project",
    "dev",
    {
        "API_KEY": "next-value",
        "TIMEOUT": "30",
    },
)

compatibility_result = client.Secrets.update(
    "my-project",
    "dev",
    secrets={
        "API_KEY": "rotated-value",
        "TIMEOUT": "60",
    },
)
```

`set` and `set_many` are the preferred write methods. `update(...)` remains available for compatibility.

### Download

```python
as_json = client.secrets.download("my-project", "dev", format="json")
as_env = client.secrets.download(
    "my-project",
    "dev",
    format="env",
    secrets=["API_KEY", "TIMEOUT"],
)
```

`download(..., format="json")` and `download(..., format="dotnet-json")` return dictionaries. Text formats such as `env`, `yaml`, `docker`, and `env-no-quotes` return strings.

## Compatibility

These compatibility paths are still preserved:

- `client.Secrets` returns the same cached object as `client.secrets`
- `Secrets` remains a top-level compatibility alias
- `SecretsClient` remains a top-level export

Example:

```python
from better_python_doppler import Doppler

client = Doppler(service_token="dp.st.example-token")
assert client.Secrets is client.secrets
```

## Exceptions

The SDK exports its own exception types:

- `DopplerError`
- `DopplerConfigError`
- `DopplerTransportError`
- `DopplerResponseError`
- `DopplerAPIError`
- `DopplerAuthError`
- `DopplerNotFoundError`
- `DopplerValidationError`

## Offline Examples

The scripts in [`examples/`](examples/) are intentionally offline. They use a fake transport so they do not call the live Doppler API.

- [`examples/direct_token_usage.py`](examples/direct_token_usage.py)
- [`examples/explicit_env_lookup.py`](examples/explicit_env_lookup.py)
- [`examples/from_env_workflow.py`](examples/from_env_workflow.py)
- [`examples/single_secret_get_set.py`](examples/single_secret_get_set.py)
- [`examples/multi_secret_set_update.py`](examples/multi_secret_set_update.py)
- [`examples/download_usage.py`](examples/download_usage.py)
- [`examples/example_secrets.py`](examples/example_secrets.py)

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
