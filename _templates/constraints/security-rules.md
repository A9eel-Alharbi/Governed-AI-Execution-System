# Security Rules Constraint Template

## Document Control

- Document ID `[required]`: `security-core`
- Owner `[required]`: `[security owner or staff engineer]`
- Last validated `[required]`: `YYYY-MM-DD`
- Stability class `[required]`: `high`

## 1. Canonical Authentication Method `[required]`

Example:
`Bearer JWT access tokens signed with RS256, paired with rotating refresh tokens stored hashed at rest.`

## 2. Authorization Model `[required]`

<!-- State one model and its role definitions. -->
Example:
`RBAC with tenant_member, tenant_admin, billing_admin, and internal_support roles.`

| Role | Allowed Actions | Forbidden Actions |
|---|---|---|
| `tenant_member` | `Read tenant-scoped resources` | `Manage billing, rotate tenant secrets` |
| `billing_admin` | `Create and change subscriptions` | `Access unrelated tenant data` |

## 3. PII Inventory `[required]`

| Field | Location | Data Class | Handling Rule |
|---|---|---|---|
| `email` | `users.email` | `PII` | `Never log in plaintext` |
| `billing_contact_name` | `tenants.billing_contact_name` | `PII` | `Encrypt at rest if persisted` |

## 4. Encryption Requirements `[required]`

Example:
- `TLS 1.2+ in transit`
- `Database volume encryption at rest`
- `Application secrets encrypted in the secret manager, never in repo`

## 5. Secrets Management `[required]`

Example:
- `Secrets are loaded from cloud secret manager at runtime.`
- `Local development uses .env files excluded from version control.`

## 6. Forbidden Patterns `[required]`

Example:
- `Hard-coded credentials`
- `Logging raw tokens`
- `Returning internal auth failure reasons to clients`
- `Building SQL with string concatenation from external input`

## 7. Required OWASP Controls `[required]`

Example:
- `A01 Broken Access Control: tenant boundary checks on every scoped endpoint`
- `A02 Cryptographic Failures: no plaintext secret persistence`
- `A03 Injection: parameterized queries only`

## 8. Prohibited Agent Actions `[required]`

Example:
- `Do not weaken authorization checks for test convenience.`
- `Do not introduce fallback auth modes not documented here.`

## Change Log

| Date | Author | Change |
|---|---|---|
| `YYYY-MM-DD` | `[name]` | `Initial draft` |
