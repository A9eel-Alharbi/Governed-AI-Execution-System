# Agent Control Stack Testing Strategy

## Document Control

- Document ID: `testing-agent-control-core`
- Owner: `Engineering Lead`
- Last validated: `2026-04-29`
- Stability class: `mixed`

## 1. Scope

Applies to restoration, balancing, case classification, policy decisioning, AOS/CDD handoff logic, and evaluation harness behavior.

## 2. Test Pyramid Targets

| Test Type | Target Range | Notes |
|---|---|---|
| `Unit` | `65% to 80%` | `Pure transformation and policy functions should dominate` |
| `Integration` | `15% to 25%` | `Registry, persistence, and AOS/CDD handoff boundaries` |
| `E2E` | `5% to 10%` | `Representative clarify, refuse, dispatch, and change-control flows` |

## 3. Coverage Thresholds by Module Type

| Module Type | Line Coverage Floor | Branch Coverage Floor | Notes |
|---|---|---|---|
| `Deterministic transforms` | `90%` | `85%` | `Restoration and contradiction logic must remain highly testable` |
| `Policy and classification modules` | `85%` | `80%` | `Boundary decisions require explicit branch coverage` |
| `Runtime adapters` | `80%` | `70%` | `AOS/CDD handoff and persistence paths` |

## 4. Test Data Management Strategy

- Evaluation fixtures are versioned in-repo.
- No test may depend on mutable external registries or remote model providers unless marked as optional comparison runs.

## 5. Forbidden Test Patterns

- Treating regression-only snapshots as proof of semantic correctness
- Counting any tool call as success when the expected safe outcome was clarification or refusal
- Hiding model-provider failures inside aggregate evaluation metrics

## 6. CI Gate Requirements

- Unit and integration suites must pass before merge.
- Registry and decision-envelope schema validation must pass for changed governed artifacts.
- Safe-outcome regression beyond approved threshold blocks merge for evaluation dataset changes.

## 7. Mutation Testing Requirements

- Required: `no`
- Reason: property and contradiction tests provide higher immediate value in phase one

## 8. Performance Test Requirements

- Deterministic preprocessing latency must be benchmarked.
- Dispatch paths into governed runtime require at least one measured throughput or latency target.

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-29` | `OpenAI Codex` | `Initial example` |
