# Project Structure

```text
Better-Python-Doppler/
|-- .github/workflows/           # CI and publish automation
|-- examples/                    # Offline example scripts using a fake transport
|-- src/
|   `-- better_python_doppler/
|       |-- __init__.py          # Public package exports
|       |-- doppler_sdk.py       # `Doppler` client
|       |-- exceptions.py        # SDK-specific exception types
|       |-- secret.py            # Top-level `Secrets` / `SecretsClient` compatibility exports
|       |-- transport.py         # Requests-backed transport boundary
|       |-- apis/
|       |   |-- __init__.py
|       |   `-- secret_apis.py   # Low-level secrets endpoint wrappers
|       |-- models/
|       |   |-- __init__.py
|       |   `-- secret.py        # Typed secret models
|       `-- resources/
|           |-- __init__.py
|           `-- secrets.py       # High-level secrets client
|-- tests/                       # Unit tests and compatibility coverage
|-- DEVELOPMENT_PLAN.md          # Phase-by-phase implementation plan
|-- PROJECT_OUTLINE.md           # Scope and product direction
|-- pyproject.toml               # Build, metadata, and test configuration
|-- README.md                    # User-facing documentation
`-- STRUCTURE.md                 # This file
```

The package is intentionally secrets-first today. `Doppler` owns auth and transport setup, `resources/secrets.py` exposes the supported public secrets workflows, `apis/secret_apis.py` contains the low-level request shape, and `transport.py` keeps HTTP concerns isolated from resource logic.
