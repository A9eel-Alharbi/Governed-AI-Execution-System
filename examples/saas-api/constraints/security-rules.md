# SaaS API Security Rules

## Document Control

- Document ID: `security-saas-core`
- Owner: `Security Lead`
- Last validated: `2026-04-28`
- Stability class: `high`

## 1. Canonical Authentication Method

Bearer JWT access tokens signed with RS256. Refresh tokens are rotated and stored hashed at rest.

## 2. Authorization Model

RBAC with `tenant_member`, `tenant_admin`, `billing_admin`, and `internal_support`.

| Role | Allowed Actions | Forbidden Actions |
|---|---|---|
| `tenant_member` | `Read tenant-scoped resources they belong to` | `Create subscriptions, access unrelated tenant data` |
| `tenant_admin` | `Read and administer tenant resources` | `Manage billing provider secrets` |
| `billing_admin` | `Create and manage subscriptions` | `Read unrelated tenant data` |
| `internal_support` | `Assist with support-only operations under audit` | `Bypass tenant scoping in production-facing APIs without explicit support path` |

## 3. PII Inventory

| Field | Location | Data Class | Handling Rule |
|---|---|---|---|
| `email` | `users.email` | `PII` | `Never log in plaintext` |
| `billing_contact_email` | `tenants.billing_contact_email` | `PII` | `Redact in logs and exports unless explicitly authorized` |

## 4. Encryption Requirements

- TLS 1.2 or higher in transit
- Database volume encryption at rest
- Provider secrets stored only in secret manager

## 5. Secrets Management

- JWT signing keys and Stripe secrets are loaded from approved secret manager at runtime.
- Local development secrets live in uncommitted `.env` files only.

## 6. Forbidden Patterns

- Hard-coded credentials
- Logging passwords, raw JWTs, or provider secrets
- Returning internal auth failure reason strings to clients
- Dynamic SQL built from external input

## 7. Required OWASP Controls

- `A01 Broken Access Control`: tenant boundary checked on every tenant-scoped endpoint
- `A02 Cryptographic Failures`: no plaintext secret persistence
- `A03 Injection`: parameterized queries only

## 8. Prohibited Agent Actions

- Do not weaken role checks for test convenience.
- Do not add fallback auth modes not defined here.

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-28` | `OpenAI Codex` | `Initial example` |
