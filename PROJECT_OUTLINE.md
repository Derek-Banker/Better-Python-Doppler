# Better Python Doppler: Project Outline

## Purpose

Better Python Doppler exists to provide a lightweight, simple, and publishable Python SDK for Doppler, with secrets management as the primary use case.

The project was created because the official Python SDK and its documentation were not reliable enough for straightforward day-to-day use. This SDK is meant to prioritize:

- Clear and predictable behavior
- Strong IDE and typing support
- Minimal conceptual overhead
- A small public API that maps cleanly to real user workflows

## Primary Goal

Make it easy to read, set, update, delete, and export Doppler secrets from Python with as little friction as possible.

## Primary User

The main user is the project author, but the package should be clean enough for public use through PyPI.

That means the design should optimize for practical simplicity first, without cutting corners that would make the package brittle or confusing for outside users.

## Current Scope

The current repo is secrets-first. That is intentional.

High-priority supported workflows:

- Retrieve a single secret value
- Retrieve a secret with metadata
- List secret names
- List all secrets in a config
- Set one secret
- Set multiple secrets
- Delete a secret
- Update a secret note
- Download secrets in supported Doppler formats

## Product Positioning

This project is not trying to be a massive all-in-one Doppler client on day one.

It should be:

- Smaller than a general-purpose SDK
- Easier to understand than raw HTTP requests
- Safer and more maintainable than a one-off script
- Structured so additional Doppler resource areas can be added later without redesigning the package

## Design Principles

- Secrets are the center of the SDK.
- The public API should stay small and obvious.
- Sync behavior is the default and current priority.
- Internal structure should be async-capable later without breaking the package shape.
- Resource logic should not be tightly coupled to a specific HTTP library.
- Convenience is good, but hidden magic is not.

## Key Design Decisions

### 1. Sync now, async-capable later

The first supported execution model is synchronous. Calls should block until the request completes.

This fits the main use cases:

- scripts
- automation
- internal tooling
- administrative tasks
- backend setup flows

The internal architecture should still separate transport concerns from resource logic so an async transport can be introduced later without rewriting the entire SDK.

### 2. Keep `.env` support, but make it explicit

`.env` support is useful and should remain supported.

What should change is where it lives.

The core client constructor should not silently own environment loading behavior in a way that complicates packaging and testing. Instead, `.env` support should be provided through an explicit convenience path, such as:

- a helper function
- a classmethod like `Doppler.from_env(...)`
- an optional auth utility module

This keeps the base client predictable while still supporting the preferred workflow of storing the service token in a `.env` file.

### 3. Secrets-first public API

The main public API should focus on ergonomic secrets access rather than exposing raw Doppler response objects.

Examples of the intended direction:

```python
client = Doppler(service_token="dp.st.XXX")

raw_value = client.secrets.get_raw("my-project", "dev", "API_KEY")
secret = client.secrets.get("my-project", "dev", "API_KEY")

client.secrets.set("my-project", "dev", "API_KEY", "new-value")
client.secrets.set_many("my-project", "dev", {
    "API_KEY": "new-value",
    "TIMEOUT": "30",
})

all_secrets = client.secrets.as_dict("my-project", "dev")
```

Optional scoped usage may be added later:

```python
cfg = client.secrets.scope(project="my-project", config="dev")
cfg.set("API_KEY", "new-value")
value = cfg.get_raw("API_KEY")
```

### 4. Publishable and testable by default

If the package cannot be installed cleanly in a fresh environment, the project is not ready.

That means:

- runtime dependencies must be declared correctly
- tests must exist before major refactors
- transport behavior must be mockable
- packaging and release flow must match the actual package state

## Intended Functionality

### Core Secrets Functionality

- `get`
  - Return a structured secret model
- `get_raw`
  - Return the plain raw secret value
- `list`
  - Return structured secret models for a config
- `list_names`
  - Return secret names only
- `as_dict`
  - Return `{secret_name: raw_value}` for convenient app usage
- `set`
  - Set one secret
- `set_many`
  - Set multiple secrets in one request
- `delete`
  - Delete a secret
- `update_note`
  - Update a secret note
- `download`
  - Download secrets in Doppler-supported output formats

### Authentication Functionality

- Direct token input
- Environment variable lookup
- Explicit `.env`-backed token loading convenience

### Error Handling

The package should raise SDK-specific exceptions instead of leaking raw `requests` exceptions and raw HTTP failures directly into user code whenever possible.

Example target exception categories:

- `DopplerError`
- `DopplerAuthError`
- `DopplerNotFoundError`
- `DopplerValidationError`
- `DopplerAPIError`

## Intended Internal Architecture

### Public Layer

- `Doppler` client
- `client.secrets` resource client
- lightweight secret models

### Resource Layer

- one resource module per Doppler resource area
- `SecretsClient` implemented first
- future clients for projects, configs, and environments

### Transport Layer

- one sync transport abstraction first
- responsible for:
  - base URL handling
  - auth headers
  - timeout defaults
  - session reuse
  - request execution
  - error mapping

This is the layer that makes future async support possible.

### Model Layer

- typed secret models
- simple data-focused structures
- no unnecessary framework dependency

## Non-Goals

These are not current priorities:

- Full parity with every Doppler endpoint
- Async client in the first refactor
- Heavy abstraction for every possible Doppler concept
- Complex configuration systems
- Hidden background concurrency
- Framework-specific integrations

## Current Problems To Address

- Packaging metadata is incomplete
- Runtime dependencies are not properly declared
- `.env` loading is mixed into the core client path
- HTTP behavior is duplicated across API modules
- No centralized timeouts, retries, or error translation
- No test suite
- Public API ergonomics are weaker than they need to be for secrets-first usage
- Some correctness issues exist in the current models and auth handling
- The repo structure suggests future expansion, but the supported public surface does not yet match that intent

## Near-Term Target State

After the next transformation pass, the repo should provide:

- a stable sync secrets client
- clean packaging and installation
- correct dependency declaration
- explicit `.env` support
- centralized transport behavior
- SDK-level exceptions
- tests for core secrets workflows
- clearer docs and examples

## Future Expansion Plan

Once the secrets client is stable, additional resource areas can be added in this order:

1. Projects
2. Configs
3. Environments

Those should only be added when they meet the same bar as secrets:

- clear use case
- ergonomic public API
- tests
- typed outputs where worthwhile
- good docs

## Success Criteria

The project is succeeding if:

- installing from PyPI works in a clean environment
- the common secrets workflows are faster to write than raw requests
- the API is easy to understand without reading source code
- tests cover core behavior and parsing
- the codebase can grow beyond secrets without another structural rewrite
