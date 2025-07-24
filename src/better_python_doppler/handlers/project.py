import requests

from requests import Response
from datetime import datetime as DateTime

class Project:

    def __init__(
            self,
            id: str | None = None,
            name: str | None = None,
            description: str | None = None,
            created_at: DateTime | None = None,
        ) -> None:
        
        self._id:           str | None         = id
        self._name:         str | None         = name
        self._description:  str | None         = description
        self._created_at:   DateTime | None    = created_at

    @property
    def id(self) -> str | None:
        return self._id
    
    @property
    def name(self) -> str | None:
        return self._name
    
    @property
    def description(self) -> str | None:
        return self._description
    
    @property
    def created_at(self) -> DateTime | None:
        return self._created_at
# -----------------------------
# PROJECT METHODS
# -----------------------------

def list_projects(auth: str, page: int = 1, per_page: int = 20) -> Response:

    url = f"https://api.doppler.com/v3/projects?page={page}&per_page={per_page}"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth}"
        }

    response = requests.get(url, headers=headers)
    return response

def get_project(auth: str, project_name: str) -> Response:
    url = f"https://api.doppler.com/v3/projects/project?project={project_name}"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {auth}"
        }

    response = requests.get(url, headers=headers)
    return response