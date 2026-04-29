# Security Threat Model

## Document Control

- Document ID: `threat-model-core`
- Owner: `Security Lead`
- Last validated: `2026-01-01`
- Stability class: `high`

## 1. System Scope

- Primary assets:
- Trusted operator roles:
- Sensitive execution surfaces:

## 2. Trust Boundaries

- External request boundary:
- Policy decision boundary:
- Repository execution boundary:
- Persistence and reporting boundary:

## 3. Key Threats

| Threat | Surface | Failure Mode | Required Mitigation |
|---|---|---|---|
| `Prompt/intent ambiguity abuse` | `interpretation` | `unsafe action from ambiguous request` | `clarify before dispatch` |
| `Policy bypass` | `dispatch and execution` | `high-risk case executes without approval` | `policy artifact enforcement and CI gate` |
| `Path traversal` | `executor and run retrieval` | `out-of-repo file access` | `repository-root path confinement` |
| `Secret disclosure` | `logs, traces, persistence` | `credential leakage` | `redaction and protected-resource checks` |
| `Constraint drift` | `work-package execution` | `execution against stale rules` | `vault health and CCR flow` |

## 4. Assumptions

- Policy artifacts are version-controlled and reviewed.
- Operators do not have direct permission to bypass protected-resource checks.
- Session loaders are validated before governed execution.

## 5. Open Risks

- Add concrete deployment-specific threats here.
- Add dependency and infrastructure threats here.

## 6. Required Review Triggers

- New protected-resource class
- New execution procedure
- New persistence surface
- New external integration

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-01-01` | `OpenAI Codex` | `Initial template` |
