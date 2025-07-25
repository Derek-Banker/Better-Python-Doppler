"""Example for listing secrets for a config."""
from better_python_doppler import Doppler

sdk = Doppler(service_token="YOUR_TOKEN")

resp = sdk.project("your-project").config("dev").secrets().list()
print(resp.json())
