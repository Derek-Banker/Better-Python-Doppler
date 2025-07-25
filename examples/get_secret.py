"""Example for retrieving a single secret using the fluent interface."""
from better_python_doppler import Doppler

# Replace with your service token
sdk = Doppler(service_token="YOUR_TOKEN")

resp = sdk.project("your-project").config("dev").secrets().get("SECRET_NAME")
print(resp.json())
