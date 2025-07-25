# Project Structure

```
Better-Python-Doppler/
├── examples/                  # Sample code demonstrating usage
│   └── example_secrets.py     # Basic secrets workflow
├── src/
│   └── better_python_doppler/
│       ├── __init__.py        # Package exports
│       ├── doppler_sdk.py     # High level `Doppler` class
│       ├── secret.py          # `Secrets` interface built on the APIs
│       ├── apis/              # Low level HTTP wrappers
│       │   ├── __init__.py
│       │   ├── config_apis.py
│       │   ├── environment_apis.py
│       │   ├── project_apis.py
│       │   └── secret_apis.py
│       ├── models/            # Typed models used by the SDK
│       │   ├── secret.py
│       │   └── ... (deprecated models)
│       └── utilities/
│           ├── __init__.py
│           └── utilities.py   # Helper functions
├── pyproject.toml             # Build and metadata configuration
├── README.md                  # Project overview and usage
└── STRUCTURE.md               # This file
```

The main entry point is the `Doppler` class which creates a service-token authenticated client. Secrets operations are exposed through `Doppler.Secrets`. All HTTP calls are made by the modules in `src/better_python_doppler/apis` and responses are converted into data classes defined in `src/better_python_doppler/models`.