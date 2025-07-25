import requests

from requests import Response
from datetime import datetime as DateTime

from .project import Projects

class Environments:

    def __init__(
            self,
            id: str | None = None,
            name: str | None = None,
            project: Projects = Projects(),
            created_at: DateTime | None = None,
            initial_fetch_at: DateTime | None = None,
        ) -> None:
        
        self._id:               str | None      = id
        self._name:             str | None      = name
        self._project:          Projects         = project
        self._created_at:       DateTime | None = created_at
        self._initial_fetch_at: DateTime | None = initial_fetch_at


    @property
    def id(self) -> str | None:
        return self._id
    
    @property
    def name(self) -> str | None:
        return self._name
    
    @property
    def project(self) -> Projects:
        return self._project
    
    @property
    def created_at(self) -> DateTime | None:
        return self._created_at
    
    @property
    def initial_fetch_at(self) -> DateTime | None:
        return self._initial_fetch_at

# -----------------------------
# API METHODS
# -----------------------------

def list_environments(auth: str, project_name: str) -> Response:
    url = f"https://api.doppler.com/v3/environments?project={project_name}"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth}"
        }

    response = requests.get(url, headers=headers)
    return response

def get_environment(auth: str, project_name: str, environment_name: str) -> Response:
    url = f"https://api.doppler.com/v3/environments/environment?project={project_name}&environment={environment_name}"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth}"
    }

    response = requests.get(url, headers=headers)
    return response