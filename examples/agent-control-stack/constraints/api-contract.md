# Agent Control Stack API Contract Companion

## Document Control

- Document ID: `api-agent-control-core`
- Owner: `API Lead`
- Last validated: `2026-04-29`
- Stability class: `mixed`
- Canonical source: `examples/agent-control-stack/constraints/openapi.yaml`

## 1. API Surface Covered

Request interpretation, decision-envelope retrieval, and AOS/CDD execution handoff initiation for registered software-delivery cases.

## 2. Endpoint Inventory

| Method | Path | Auth Method | Versioning Rule | Stability | Notes |
|---|---|---|---|---|---|
| `POST` | `/v1/interpretations` | `Bearer JWT` | `URI versioned` | `low` | `Run restore, balance, classify, and policy decision for one request` |
| `GET` | `/v1/interpretations/{decisionId}` | `Bearer JWT` | `URI versioned` | `low` | `Fetch a decision envelope and trace` |
| `POST` | `/v1/execution-handoffs` | `Bearer JWT` | `URI versioned` | `low` | `Dispatch an approved case into an AOS/CDD target` |
| `POST` | `/v1/cases/validate` | `Bearer JWT` | `URI versioned` | `mixed` | `Check whether a candidate case is registered, blocked, or requires escalation` |

## 3. Naming Translation Convention

- Database columns use `snake_case`.
- Public API fields use `camelCase`.
- The agent must treat `policy_decision -> policyDecision`, `case_id -> caseId`, and `dispatch_target -> dispatchTarget` as intentional naming translations, not contradictions.

## 4. Error Contract Rules

- `400` validation failure
- `401` authentication failure
- `403` authorization failure
- `404` unknown decision or handoff target
- `409` contradiction or registry conflict
- `422` ambiguous request that requires clarification before dispatch

## 5. Prohibited Agent Actions

- Do not collapse `422 clarify required` into generic `400`.
- Do not dispatch execution from `/v1/interpretations` as a side effect.
- Do not add implicit "best effort" mode that bypasses registry or policy gates.

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-29` | `OpenAI Codex` | `Initial example` |
