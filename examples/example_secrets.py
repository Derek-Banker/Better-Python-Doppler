# === BOILER PLATE SUPPORT ==============

import os
from dotenv import load_dotenv
load_dotenv()

SERVICE_TOKEN = os.getenv("SERVICE_TOKEN")
PROJECT_NAME = os.getenv("PROJECT_NAME")
CONFIG_NAME = os.getenv("CONFIG_NAME")
SECRET_NAME = os.getenv("SECRET_NAME")

# === BOILER PLATE SUPPORT ==============

from better_python_doppler import Doppler

doppler = Doppler(service_token=SERVICE_TOKEN)

doppler.Secrets.list_names(PROJECT_NAME, CONFIG_NAME) 