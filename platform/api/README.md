# Platform API

This service is the product backend for the hosted AOS/CDD platform.

It is responsible for:

- project state
- repo connection metadata
- calling `agent_control_stack`
- exposing product-facing endpoints to the website

## Planned Responsibilities

- `GET /health`
- `GET /projects`
- `POST /projects`
- `POST /runs/interpret`
- `POST /runs/execute`

## Run Locally

```powershell
python -m pip install -e .
uvicorn app.main:app --reload --port 8100
```

## Database Backends

The API now supports two backend modes behind the same store interface:

- default local mode: SQLite at `platform/api/data/platform.db`
- production-oriented mode: PostgreSQL via `AOS_CDD_PLATFORM_DATABASE_URL`

Example:

```powershell
$env:AOS_CDD_PLATFORM_DATABASE_URL="postgresql://user:pass@localhost:5432/aos_cdd_platform"
uvicorn app.main:app --reload --port 8100
```

If the configured backend is unavailable in the current environment, the store falls back to in-memory seeded state so local development does not hard-fail.

## External Authentication Mode

The API can also run behind an external auth gateway.

Environment variables:

```powershell
$env:AOS_CDD_PLATFORM_AUTH_MODE="external"
$env:AOS_CDD_PLATFORM_AUTH_PROVIDER="Proxy Auth"
$env:AOS_CDD_PLATFORM_AUTH_LOGIN_PATH="/login"
```

Trusted user headers expected by default:

- `X-Platform-User-Id`
- `X-Platform-User-Email`
- `X-Platform-User-Name`
- `X-Platform-User-Role`

Those header names can be overridden with:

- `AOS_CDD_PLATFORM_AUTH_USER_ID_HEADER`
- `AOS_CDD_PLATFORM_AUTH_USER_EMAIL_HEADER`
- `AOS_CDD_PLATFORM_AUTH_USER_NAME_HEADER`
- `AOS_CDD_PLATFORM_AUTH_USER_ROLE_HEADER`
