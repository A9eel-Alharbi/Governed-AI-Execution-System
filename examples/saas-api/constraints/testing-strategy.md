# SaaS API Testing Strategy

## Document Control

- Document ID: `testing-saas-core`
- Owner: `Engineering Lead`
- Last validated: `2026-04-28`
- Stability class: `mixed`

## 1. Scope

Applies to public API handlers, service modules, background jobs, and integration flows in the SaaS API example.

## 2. Test Pyramid Targets

| Test Type | Target Range | Notes |
|---|---|---|
| `Unit` | `60% to 75%` | `Logic-heavy services and adapters` |
| `Integration` | `20% to 30%` | `Database, auth, and provider boundaries` |
| `E2E` | `5% to 10%` | `Critical login and subscription flows only` |

## 3. Coverage Thresholds by Module Type

| Module Type | Line Coverage Floor | Branch Coverage Floor | Notes |
|---|---|---|---|
| `Service modules` | `85%` | `75%` | `Public logic paths must be directly exercised` |
| `Route handlers` | `80%` | `70%` | `Validation and authorization paths required` |
| `Background jobs` | `80%` | `70%` | `Success, retry, and idempotency paths required` |

## 4. Test Data Management Strategy

- Integration tests use disposable database fixtures.
- No test may depend on mutable shared remote infrastructure.

## 5. Forbidden Test Patterns

- Tests against production infrastructure
- Assertions on status code only for contract-bearing endpoints
- Sleep-based eventual consistency tests without bounded rationale

## 6. CI Gate Requirements

- Unit and integration suites must pass before merge.
- Coverage regressions below module floor block merge.
- Contract validation must run for changed API artifacts.

## 7. Mutation Testing Requirements

- Required: `no`
- Reason: not mandatory for this example repository

## 8. Performance Test Requirements

- Public endpoints and high-volume jobs require at least one benchmark or measured target in their WP done criteria.

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-28` | `OpenAI Codex` | `Initial example` |
