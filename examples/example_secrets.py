# === BOILER PLATE SUPPORT ==============

import os
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime as DateTime

SERVICE_TOKEN = os.getenv("SERVICE_TOKEN")
PROJECT_NAME = os.getenv("PROJECT_NAME")
CONFIG_NAME = os.getenv("CONFIG_NAME")

var_list = [SERVICE_TOKEN, PROJECT_NAME, CONFIG_NAME]

if (    SERVICE_TOKEN   is None  
    or  PROJECT_NAME    is None 
    or  CONFIG_NAME     is None):
    raise ValueError

# === BOILER PLATE SUPPORT ==============

from better_python_doppler import Doppler

doppler = Doppler(service_token=SERVICE_TOKEN)

names = doppler.Secrets.list_names(PROJECT_NAME, CONFIG_NAME)

list_secrets = doppler.Secrets.list(PROJECT_NAME, CONFIG_NAME)

print(doppler.Secrets.get(PROJECT_NAME, CONFIG_NAME, "TEST_GET").value.raw)

doppler.Secrets.update(PROJECT_NAME, CONFIG_NAME, secrets={"TEST_SET": DateTime.strftime(DateTime.now(), "%Y-%m-%d %H:%M:%S")})

print(doppler.Secrets.get(PROJECT_NAME, CONFIG_NAME, "TEST_SET").value.raw)

doppler.Secrets.update(PROJECT_NAME, CONFIG_NAME, "TEST_SET", DateTime.strftime(DateTime.now(), "%Y-%m-%d %H:%M:%S"))

print(doppler.Secrets.get(PROJECT_NAME, CONFIG_NAME, "TEST_SET").value.raw)
