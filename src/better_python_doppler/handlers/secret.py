import requests
from typing import Literal

from requests import Response

import utils

from models import SecretModel

class Secrets:

    

# -----------------------------
# API METHODS
# -----------------------------

def list_secrets(
        auth: str, 
        project_name: str, 
        config_name: str, 
        include_dynamic_secrets: bool = False, 
        dynamic_secrets_ttl_sec: int = 1800,
        secrets: list[str] = [],
        include_managed_secrets: bool = True
    ) -> Response:

    if len(secrets) > 0:
        requested_secrets = "&secrets=" + utils.list_to_comma_string(secrets)
    else:
        requested_secrets = ""

    url = f"https://api.doppler.com/v3/configs/config/secrets?" + (
        f"project={project_name}"
        f"&config={config_name}"
        f"&include_dynamic_secrets={include_dynamic_secrets}"
        f"&dynamic_secrets_ttl_sec={dynamic_secrets_ttl_sec}"
        + requested_secrets + 
        f"&include_managed_secrets={include_managed_secrets}"
    )

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth}"
    }

    response = requests.get(url, headers=headers)
    return response

def list_secret_names(
        auth: str, 
        project_name: str, 
        config_name: str, 
        include_dynamic_secrets: bool = False, 
        include_managed_secrets: bool = True
    ) -> Response:

    url = f"https://api.doppler.com/v3/configs/config/secrets/names?" + (
        f"project={project_name}"
        f"&config={config_name}"
        f"&include_dynamic_secrets={include_dynamic_secrets}"
        f"&include_managed_secrets={include_managed_secrets}"
    )

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth}"
    }

    response = requests.get(url, headers=headers)
    return response

def get_secret(
        auth: str, 
        project_name: str, 
        config_name: str,
        secret_name: str 
    ) -> Response:
    url = f"https://api.doppler.com/v3/configs/config/secret?project={project_name}&config={config_name}&name={secret_name}"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth}"
    }

    response = requests.get(url, headers=headers)
    return response

def update_secrets(
        auth: str, 
        project_name: str, 
        config_name: str, 
        secrets: dict[str, str]
    ) -> Response:
    url = f"https://api.doppler.com/v3/configs/config/secrets"

    payload = {
        "project": project_name,
        "config": config_name,
        "secrets": secrets
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {auth}"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response

def download_secrets(
        auth: str, 
        project_name: str, 
        config_name: str,
        format: Literal["json", "dotnet-json", "env", "yaml" , "docker", "env-no-quotes"] = "json",
        name_transformer: Literal["camel", "upper-camel", "lower-snake", "tf-var", "dotnet", "dotnet-env", "lower-kebab"] | None = None,
        include_dynamic_secrets: bool = False,
        dynamic_secrets_ttl_sec: int = 1800,
        secrets: list[str] = []
    ) -> Response:

    if len(secrets) > 0:
        requested_secrets = "&secrets=" + utils.list_to_comma_string(secrets)
    else:
        requested_secrets = ""

    if name_transformer is not None:
        requested_transformer = "&name_transformer=" + name_transformer
    else:
        requested_transformer = ""

    url = f"https://api.doppler.com/v3/configs/config/secrets/download?" + (
        f"project={project_name}"
        f"&config={config_name}"
        f"&format={format}"
        + requested_transformer +
        f"&include_dynamic_secrets={include_dynamic_secrets}"
        f"&dynamic_secrets_ttl_sec={dynamic_secrets_ttl_sec}"
        + requested_secrets
    )

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth}"
    }

    response = requests.get(url, headers=headers)
    return response

def delete_secret(
        auth: str, 
        project_name: str, 
        config_name: str, 
        secret_name: str
    ) -> Response:
    url = f"https://api.doppler.com/v3/configs/config/secret?project={project_name}&config={config_name}&name={secret_name}"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth}"
    }

    response = requests.delete(url, headers=headers)
    return response

def update_note(
        auth: str, 
        project_name: str, 
        secret_name: str,
        note: str 
    ) -> Response:

    url = f"https://api.doppler.com/v3/projects/project/note?project={project_name}"

    payload = {
        "secret": secret_name,
        "note": note
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {auth}"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response
