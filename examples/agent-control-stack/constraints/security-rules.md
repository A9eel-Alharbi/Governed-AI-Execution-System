# Agent Control Stack Security Rules

## Document Control

- Document ID: `security-agent-control-core`
- Owner: `Security Lead`
- Last validated: `2026-04-29`
- Stability class: `high`

## 1. Canonical Authentication Method

Bearer JWT access tokens signed with asymmetric keys. Service-to-service calls use scoped service identities and may not reuse human operator tokens.

## 2. Authorization Model

RBAC with `operator`, `policy_admin`, `repo_executor`, and `observer`.

| Role | Allowed Actions | Forbidden Actions |
|---|---|---|
| `operator` | `Submit interpretation requests and answer clarification prompts` | `Bypass protected-resource policy or approve their own blocked escalation` |
| `policy_admin` | `Manage case registry and protected-resource rules` | `Run repository execution without an approved dispatch path` |
| `repo_executor` | `Execute approved AOS/CDD work-package sessions` | `Change registry policy directly from an execution session` |
| `observer` | `Read traces and decision envelopes` | `Trigger dispatch or modify policy` |

## 3. Sensitive Data Inventory

| Field | Location | Data Class | Handling Rule |
|---|---|---|---|
| `raw_input` | `requests.raw_input` | `Sensitive operational input` | `Retain for audit, but redact secrets and credentials from logs` |
| `decision_json` | `decision_envelopes.decision_json` | `Trace and policy evidence` | `Must not contain raw secrets, full file contents, or access tokens` |
| `trace_json` | `restoration_traces.trace_json` | `Interpretation evidence` | `Store only references and normalized context, not secret values` |

## 4. Encryption Requirements

- TLS 1.2 or higher in transit
- Encryption at rest for decision and trace persistence
- Secret material stored only in approved secret manager

## 5. Secrets Management

- API signing keys, provider credentials, and repository access tokens are loaded from secret manager at runtime.
- Local development secrets live in uncommitted `.env` files only.

## 6. Forbidden Patterns

- Silent fallback from blocked case to generic tool execution
- Direct destructive filesystem action without protected-path policy evaluation
- Logging raw bearer tokens, secret values, or unredacted credential-bearing prompts
- Allowing execution handoff creation when the source decision is `clarify` or `refuse`

## 7. Required OWASP Controls

- `A01 Broken Access Control`: role and protected-resource checks on every dispatch path
- `A02 Cryptographic Failures`: no plaintext secret persistence
- `A03 Injection`: parameterized persistence and no untrusted shell interpolation

## 7.1 Threat Model Reference

- Canonical threat model: `examples/agent-control-stack/ops/security-threat-model.md`
- Review the threat model before adding new execution procedures, persistence surfaces, or protected-resource classes.

## 8. Prohibited Agent Actions

- Do not add a bypass that lets registry-miss cases execute "for convenience."
- Do not downgrade protected-resource failures into warnings.
- Do not embed direct repository credentials in generated session artifacts.

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-29` | `OpenAI Codex` | `Initial example` |
