# === BOILER SUPPORT ===================

import os
from dotenv import load_dotenv

import requests
from requests import Response

load_dotenv()

SERVICE_TOKEN   = os.getenv("SERVICE_TOKEN")
PROJECT_NAME    = os.getenv("PROJECT_NAME")
CONFIG_NAME     = os.getenv("CONFIG_NAME")
SECRET_NAME     = os.getenv("SECRET_NAME")


# === BOILER SUPPORT ===================

import better_python_doppler.utilities as utilities



import requests
from typing import Optional
from requests import Response

def list_secrets(
    auth: str,
    project_name: str,
    config_name: str,
    include_dynamic_secrets: bool = True,
    dynamic_secrets_ttl_sec: int = 1800,
    secrets: list[str] | None = None,
    include_managed_secrets: bool = True
) -> Response:
    base_url = "https://api.doppler.com/v3/configs/config/secrets"
    params = {
        "project": project_name,
        "config": config_name,
        "include_dynamic_secrets": str(include_dynamic_secrets).lower(),
        "dynamic_secrets_ttl_sec": dynamic_secrets_ttl_sec,
        "include_managed_secrets": str(include_managed_secrets).lower(),
    }
    if secrets:
        # only add this key if the list is non-empty
        params["secrets"] = ",".join(secrets)

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {auth}",
    }
    return requests.get(base_url, headers=headers, params=params)



print(list_secrets(SERVICE_TOKEN, PROJECT_NAME, CONFIG_NAME).text)