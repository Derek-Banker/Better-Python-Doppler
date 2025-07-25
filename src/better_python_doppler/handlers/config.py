import requests

from requests import Response
from datetime import datetime as DateTime
from urllib.parse import quote as url_encode

from better_python_doppler.handlers import Project, Environment

class Config:

    def __init__(
            self,
            name: str | None = None,
            project: Project = Project(),
            environment: Environment = Environment(),
            created_at: DateTime | None = None,
            initial_fetch_at: DateTime | None = None,
            last_fetch_at: DateTime | None = None,
            root: bool | None = None,
            locked: bool | None = None
        ) -> None:
        
        self._name:             str | None      = name 
        self._project:          Project         = project
        self._environment:      Environment     = environment
        self._created_at:       DateTime | None = created_at
        self._initial_fetch_at: DateTime | None = initial_fetch_at
        self._last_fetch_at:    DateTime | None = last_fetch_at
        self._root:             bool | None     = root
        self._locked:           bool | None     = locked
    
    @property
    def name(self) -> str | None:
        return self._name
    
    @property
    def project(self) -> Project:
        return self._project
    
    @property
    def environment(self) -> Environment:
        return self._environment
    
    @property
    def created_at(self) -> DateTime | None:
        return self._created_at
    
    @property
    def initial_fetch_at(self) -> DateTime | None:
        return self._initial_fetch_at
    
    @property
    def last_fetch_at(self) -> DateTime | None:
        return self._last_fetch_at
    
    @property
    def root(self) -> bool | None:
        return self._root
    
    @property
    def locked(self) -> bool | None:
        return self._locked


# -----------------------------
# API METHODS
# -----------------------------

def list_configs(
        auth: str, 
        project_name: str, 
        environment_slug: str = "Environment slug", 
        page: int = 1, 
        per_page: int = 20
    ) -> Response:

    base_url = "https://api.doppler.com/v3/configs"
    params = {
        "project":      project_name,
        "environment":  url_encode(environment_slug),
        "page":         page,
        "per_page":     per_page
        }

    headers = {
        "accept":           "application/json",
        "authorization":    f"Bearer {auth}"
        }

    return requests.get(base_url, params, headers=headers)


def get_config(
        auth: str, 
        project_name: str, 
        config_name: str
    ) -> Response:
    
    base_url = "https://api.doppler.com/v3/configs/config"
    params = {
        "project": project_name,
        "config":  config_name
        }

    headers = {
        "accept":           "application/json",
        "authorization":    f"Bearer {auth}"
        }

    return requests.get(base_url, params, headers=headers)