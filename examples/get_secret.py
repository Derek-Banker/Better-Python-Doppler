"""Example usage of the chainable Doppler SDK."""
from better_python_doppler.doppler_sdk import Doppler

# Expect a token in the environment under DOPPLER_TOKEN
sdk = Doppler(service_token_environ_name="DOPPLER_TOKEN")
secret = sdk.project("my-project").config("dev").secrets().get("MY_SECRET")
print(secret)

