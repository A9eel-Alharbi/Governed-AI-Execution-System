# SaaS API Contract Companion

## Document Control

- Document ID: `api-saas-core`
- Owner: `API Lead`
- Last validated: `2026-04-28`
- Stability class: `mixed`
- Canonical source: `examples/saas-api/constraints/openapi.yaml`

## 1. API Surface Covered

Authentication, subscription create/fetch, usage event ingestion, and daily usage report retrieval.

## 2. Endpoint Inventory

| Method | Path | Auth Method | Versioning Rule | Stability | Notes |
|---|---|---|---|---|---|
| `POST` | `/v1/auth/login` | `none` | `URI versioned` | `high` | `Credential exchange` |
| `POST` | `/v1/subscriptions` | `Bearer JWT` | `URI versioned` | `low` | `Create subscription` |
| `GET` | `/v1/subscriptions/{subscriptionId}` | `Bearer JWT` | `URI versioned` | `low` | `Fetch subscription` |
| `POST` | `/v1/usage/events` | `Bearer JWT` | `URI versioned` | `low` | `Usage ingestion` |
| `GET` | `/v1/usage/reports/daily` | `Bearer JWT` | `URI versioned` | `low` | `Daily usage report` |

## 3. Naming Translation Convention

- Database columns use `snake_case`.
- Public API fields use `camelCase`.
- The agent must treat `tenant_id -> tenantId`, `plan_code -> planCode`, and `provider_subscription_id -> providerSubscriptionId` as intentional naming translations, not contradictions.

## 4. Error Contract Rules

- `400` validation failure
- `401` authentication failure
- `403` authorization failure
- `404` resource not found
- `409` state conflict or idempotency conflict

## 5. Prohibited Agent Actions

- Do not add undocumented response fields.
- Do not change auth method on an endpoint without approved CCR.
- Do not collapse documented error classes into one generic error.

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-28` | `OpenAI Codex` | `Initial example` |
