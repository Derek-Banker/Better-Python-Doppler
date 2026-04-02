# Better Python Doppler: Development Plan

## Objective

Transform the current secrets-focused prototype into a lightweight, publishable, tested SDK with a clean internal structure that supports future expansion beyond secrets.

This plan assumes:

- sync support now
- async-capable structure later
- secrets remain the highest priority
- `.env` support stays, but becomes explicit instead of being embedded in the core client path

## Implementation Strategy

Do not expand feature scope before stabilizing the foundation.

The correct order is:

1. Make installs reliable
2. Make behavior testable
3. Centralize HTTP logic
4. Improve secrets ergonomics
5. Preserve or manage compatibility
6. Prepare the package for later expansion

## Phase 1: Packaging And Baseline Cleanup

### Goals

- Make the package install correctly in a fresh environment
- Eliminate obvious metadata and release inconsistencies
- Define the supported dependency story clearly

### Tasks

- Update `pyproject.toml` runtime dependencies
  - add `requests`
  - add either `python-dotenv` or move `.env` support behind an optional extra
- Review Python version support and keep or adjust `>=3.12`
- Fix obvious metadata issues
  - keyword typo
  - version consistency
  - classifier quality
- Decide what to do with local `dist/` artifacts
  - remove stale artifacts from the working tree if they are misleading
  - avoid treating old built artifacts as current release truth

### Deliverables

- clean `pyproject.toml`
- clear dependency model
- installable package in a fresh environment

## Phase 2: Test Harness Before Refactor Depth

### Goals

- Lock down current and intended secrets behavior before larger structural changes
- Make future refactors safer

### Tasks

- Add a `tests/` directory
- Add test dependency configuration
- Add unit tests for:
  - client auth validation
  - token loading from direct input
  - explicit env-based loading
  - secret response parsing
  - update payload formation
  - download behavior by format
  - delete and note update calls
- Mock HTTP calls rather than hitting the live Doppler API
- Add a small compatibility test for the current `Doppler(...).Secrets` path if backward compatibility is retained

### Deliverables

- repeatable local test suite
- baseline coverage on secrets behavior

## Phase 3: Introduce A Real Transport Layer

### Goals

- Stop duplicating raw request logic across API modules
- Create a structure that supports future async transport without rewriting resource clients

### Tasks

- Add a sync transport module, for example `transport.py`
- Centralize:
  - base URL
  - auth header construction
  - request execution
  - timeout handling
  - session reuse
  - response status translation
- Define a transport interface or base protocol that resource clients depend on
- Move raw HTTP request details out of resource code
- Keep the first transport implementation sync and `requests`-backed

### Deliverables

- one shared sync transport
- no direct scattered `requests.get/post/delete(...)` in resource entrypoints

## Phase 4: Secrets API Refactor And Ergonomics

### Goals

- Make the SDK pleasant for the real use case: reading and writing secrets quickly
- Keep the public API small and obvious

### Tasks

- Introduce a dedicated secrets resource client
  - likely `client.secrets`
- Preserve `client.Secrets` temporarily as a compatibility alias if needed
- Refine method set:
  - keep `get`
  - add `get_raw`
  - keep `list`
  - keep `list_names`
  - add `as_dict`
  - replace or supplement `update` with:
    - `set`
    - `set_many`
- Keep `download`, `delete`, and `update_note`
- Normalize parameter names and argument ordering
- Ensure return types are consistent and typed

### Deliverables

- ergonomic secrets client
- clearer method naming
- cleaner return-value story

## Phase 5: Authentication And `.env` Design Cleanup

### Goals

- Keep `.env` support without coupling it to the base constructor
- Make auth behavior explicit and easier to reason about

### Tasks

- Remove implicit `.env` loading from the core constructor path
- Keep direct token construction:
  - `Doppler(service_token="...")`
- Support explicit environment lookup
- Add an explicit convenience path for `.env`, such as:
  - `Doppler.from_env("SERVICE_TOKEN")`
  - or `load_service_token(...)` helper
- Decide whether `.env` support is:
  - a required dependency
  - or an optional extra

### Deliverables

- predictable auth behavior
- retained `.env` workflow
- better testability

## Phase 6: Exceptions And Correctness Fixes

### Goals

- Replace vague failures with clear SDK errors
- Fix known correctness issues while the structure is being cleaned up

### Tasks

- Add SDK exception classes
- Translate common HTTP errors into SDK exceptions
- Fix shared mutable default values in models
- Clean up invalid or weak `ValueError` construction
- Review model defaults and typing behavior
- Review response parsing assumptions for missing fields

### Deliverables

- safer failure modes
- cleaner model behavior
- more trustworthy API surface

## Phase 7: Docs And Example Refresh

### Goals

- Make the project understandable without reading source
- Reflect the actual supported API, not an aspirational one

### Tasks

- Update `README.md`
- Add examples for:
  - direct token usage
  - explicit env lookup
  - explicit `.env` workflow
  - single-secret set/get
  - multi-secret update
  - download usage
- Document current scope honestly
- Link to the project outline and development plan

### Deliverables

- accurate README
- realistic examples
- onboarding path for outside users

## Phase 8: Release Readiness

### Goals

- Ensure the package is actually ready to publish

### Tasks

- Validate build output
- Validate install in a clean environment
- Run tests in CI before publish
- Review publish workflow assumptions
- Confirm versioning strategy

### Deliverables

- publishable release process
- CI gate before packaging and release

## Future Phases After Secrets Stabilization

These phases should not begin until the secrets client is solid.

### Phase 9: Projects Client

- Add a typed public projects resource client only if there is a real workflow behind it

### Phase 10: Configs Client

- Add config operations with the same standards as secrets

### Phase 11: Environments Client

- Add environment operations with the same standards as secrets

### Phase 12: Async Support

- Add an async transport implementation
- Add async resource clients only if the use cases justify the maintenance cost
- Avoid breaking the existing sync API

## Recommended File Structure Target

```text
src/better_python_doppler/
  __init__.py
  client.py
  transport.py
  exceptions.py
  resources/
    __init__.py
    secrets.py
  models/
    __init__.py
    secrets.py
  auth/
    __init__.py
    env.py
tests/
  test_client.py
  test_secrets.py
  test_transport.py
  test_auth.py
```

## Suggested Execution Order

1. Packaging cleanup
2. Add tests around current secrets behavior
3. Add transport layer
4. Refactor secrets client onto transport
5. Improve auth and `.env` flow
6. Add exceptions and fix correctness issues
7. Refresh docs and examples
8. Validate release pipeline

## Risks To Watch

- Breaking the current public API more than necessary
- Keeping `.env` support too magical
- Overengineering for future async before the sync client is stable
- Expanding into projects/configs/environments too early
- Writing tests after refactor instead of before it

## Definition Of Done For The Transformation

The transformation is complete when:

- the package installs cleanly
- secrets workflows are ergonomic
- `.env` support is explicit and reliable
- transport logic is centralized
- tests exist and pass
- docs match reality
- the codebase can add new Doppler resource clients without another redesign
