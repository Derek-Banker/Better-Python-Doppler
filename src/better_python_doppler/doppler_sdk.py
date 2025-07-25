# src\better_python_doppler\doppler_sdk.py

from datetime import datetime as DateTime

from handlers import Projects, Environments, Configs, Secrets

class Doppler:

    def __init__(
            self,
            service_token: str | None = None,
            service_token_environ_name: str | None = None
        ) -> None:

        self._service_token = self._get_service_token(service_token, service_token_environ_name)

        # self.environments =  Environments()
        # self.environments =  Configs()
        # self.environments =  Secrets()


    def _get_service_token(
            self, 
            service_token: str | None = None,
            service_token_environ_name: str | None = None
        ) -> str:

        if (service_token is None) == (service_token_environ_name is None):
            raise ValueError("Either `service_token` OR `service_token_environ_name` must be provided upon init. NOT both or neither.") 
        
        if service_token is not None:
            return service_token
        else:
            import os
            from dotenv import load_dotenv
            load_dotenv()

            pulled_token = os.getenv(service_token_environ_name) # type: ignore

            if pulled_token is None:
                raise ValueError("Attempting to retrieve the environmental variable named `%s` returns `None`.", service_token_environ_name)    

            return pulled_token
        
    def Project(
            self,
            id: str | None = None,
            name: str | None = None,
            description: str | None = None,
            created_at: DateTime | None = None
        ) -> Projects:

        self.projects = Projects(id, name, description, created_at)
        return self.projects

    def Environment(self,
            id: str | None = None,
            name: str | None = None,
            project: Projects = Projects(),
            created_at: DateTime | None = None,
            initial_fetch_at: DateTime | None = None
        ) -> Environments:
        
        self.environments = Environments(id, name, project, created_at, initial_fetch_at)
        return self.environments

    def Config(
            self,
            name: str | None = None,
            project: Projects = Projects(),
            environment: Environments = Environments(),
            created_at: DateTime | None = None,
            initial_fetch_at: DateTime | None = None,
            last_fetch_at: DateTime | None = None,
            root: bool | None = None,
            locked: bool | None = None
        ) -> Configs:
        
        self.configs = Configs(name, project, environment, created_at, initial_fetch_at, last_fetch_at, root, locked)
        return self.configs

    def Secrets(self) -> Secrets:     
