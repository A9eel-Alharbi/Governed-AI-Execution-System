# Agent Control Stack Security Threat Model

## Document Control

- Document ID: `threat-model-agent-control-core`
- Owner: `Security Lead`
- Last validated: `2026-04-29`
- Stability class: `high`

## 1. System Scope

- Primary assets: `decision envelopes`, `policy artifacts`, `session loaders`, `persisted run reports`
- Trusted operator roles: `operator`, `policy_admin`, `repo_executor`, `observer`
- Sensitive execution surfaces: `protected-resource dispatch`, `repository-root file access`, `run retrieval API`

## 2. Trust Boundaries

- External request boundary: raw user requests enter through CLI or HTTP and must not be treated as implicitly safe
- Policy decision boundary: case classification and policy resolution decide whether execution is allowed
- Repository execution boundary: executor may only operate within `repository_root`
- Persistence and reporting boundary: persisted runs and reports may contain sensitive operational traces

## 3. Key Threats

| Threat | Surface | Failure Mode | Required Mitigation |
|---|---|---|---|
| `Ambiguous request abuse` | `interpretation` | `unsafe dispatch from vague prompt` | `clarify path and policy-critical eval coverage` |
| `Policy bypass` | `dispatch and CI` | `high-risk execution without approved policy state` | `policy profile enforcement and policy gate` |
| `Path traversal` | `executor and run store` | `out-of-repo read/write access` | `repository-root confinement and run-id validation` |
| `Secret disclosure` | `protected-resource handling` | `secret file access or leakage in traces` | `fail-closed protected-resource policy and redaction rules` |
| `Constraint drift` | `AOS/CDD handoff` | `execution against stale or conflicting artifacts` | `vault health, session validation, and CCR flow` |

## 4. Assumptions

- Governed policy artifacts are reviewed before merge.
- Session loaders are validator-backed before execution.
- Protected-resource cases require explicit privilege context and may still escalate.

## 5. Open Risks

- No production deployment isolation model is described yet.
- Long-term retention policy for persisted runs is still operationally lightweight.
- Dependency-level supply-chain review is not yet formalized in this repo.

## 6. Required Review Triggers

- New protected-resource category
- New execution procedure
- New API endpoint that persists or returns governed traces
- New persistence backend beyond local filesystem

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-29` | `OpenAI Codex` | `Initial example` |
