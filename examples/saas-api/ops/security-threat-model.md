# SaaS API Security Threat Model

## Document Control

- Document ID: `threat-model-saas-core`
- Owner: `Security Lead`
- Last validated: `2026-04-28`
- Stability class: `high`

## 1. System Scope

- Primary assets: `tenant data`, `subscription records`, `provider credentials`, `JWT signing keys`
- Trusted operator roles: `tenant_admin`, `billing_admin`, `internal_support`
- Sensitive execution surfaces: `subscription creation`, `provider sync`, `support access paths`

## 2. Trust Boundaries

- Client boundary: external API callers supply tenant-scoped input
- Application boundary: service enforces tenant and billing roles
- Provider boundary: billing provider callbacks and sync jobs affect local state
- Support boundary: internal support actions must stay auditable and scoped

## 3. Key Threats

| Threat | Surface | Failure Mode | Required Mitigation |
|---|---|---|---|
| `Broken tenant isolation` | `API authorization` | `cross-tenant data access` | `role and tenant boundary checks on every endpoint` |
| `Secret exposure` | `provider integration` | `provider key leakage` | `secret manager only and log redaction` |
| `Schema drift after CCR` | `WP execution` | `implementation targets stale contract` | `vault health, CCR artifacts, and blocked sessions` |
| `Replay or duplicate sync` | `provider callbacks/jobs` | `duplicate subscription state changes` | `idempotency and human review for failure recovery` |
| `Unsafe support bypass` | `internal support path` | `unscoped production data access` | `support-specific audit path and approval discipline` |

## 4. Assumptions

- Production credentials are never stored in the repo.
- Support access uses dedicated audited flows.
- Constraint documents are the authoritative source of schema and API behavior.

## 5. Open Risks

- End-to-end infrastructure threat coverage is not modeled in this example.
- Third-party outage and failover threats are only partially addressed.

## 6. Required Review Triggers

- New billing provider integration
- New support-only endpoint
- New tenant-scoped data class
- New background worker that mutates billing state

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-28` | `OpenAI Codex` | `Initial example` |
