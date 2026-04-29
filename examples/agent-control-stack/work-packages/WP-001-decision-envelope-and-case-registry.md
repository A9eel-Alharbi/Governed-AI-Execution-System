# Work Package WP-001

## Document Control

- WP ID: `WP-001`
- Title: `Implement decision envelope and initial case registry`
- Owner: `Platform Lead`
- Last validated: `2026-04-29`
- Parent ticket: `ACS-001`
- Status: `ready`

## 1. Dependencies

- Depends on: `none`
- Blocked by: `none`

## 2. Stability Classification

- Referenced constraint stability: `mixed`

## 3. In Scope

- Implement the typed decision envelope with top-level outcomes `clarify`, `refuse`, `dispatch`, and `escalate`
- Implement the initial case registry for `new_project.initial_definition`, `implementation.create_first_wp`, `implementation.run_wp`, and `change.constraint_conflict`
- Implement policy validation that blocks unknown cases and protected-resource dispatches missing required policy dimensions
- Add unit tests for successful classification, registry miss refusal, contradiction stop behavior, and protected-resource fail-closed behavior

## 4. Out of Scope

- No hosted multi-tenant control plane
- No automatic work-package authoring beyond first-case routing decisions
- No direct execution of repository tools
- No new case families beyond the four listed in scope

## 5. Constraint Documents To Load

| Document | Sections | Permission |
|---|---|---|
| `constraints/schema.md` | `decision_envelopes table, case_registrations table, Protected Fields and Prohibited Agent Actions` | `READ-ONLY` |
| `constraints/openapi.yaml` | `paths./v1/interpretations, paths./v1/cases/validate, paths./v1/execution-handoffs` | `READ-ONLY` |
| `constraints/api-contract.md` | `Error Contract Rules, Prohibited Agent Actions` | `READ-ONLY` |
| `constraints/security-rules.md` | `Authorization Model, Forbidden Patterns, Prohibited Agent Actions` | `READ-ONLY` |
| `constraints/testing-strategy.md` | `Coverage Thresholds by Module Type, Forbidden Test Patterns` | `READ-ONLY` |
| `constraints/vision.md` | `In Scope, Out of Scope, Architecture Direction Decisions` | `ADVISORY` |

## 6. Done Criteria

- `Decision conformance: every execution path returns exactly one allowed top-level outcome and no fallback outcome values`
- `Registry conformance: unregistered cases return refuse or escalate and never dispatch`
- `Protected-resource policy: dispatch is denied when required policy dimensions are missing`
- `Traceability: decision envelope links raw request, classification result, and dispatch target or refusal reason`
- `Coverage: unit tests cover success, contradiction, registry miss, and protected-resource fail-closed scenarios`

## 7. Complexity

- Estimated complexity: `M`

## 8. WP Size Validation

- [x] `Touches one concern, not an entire feature slice`
- [x] `Touches no more files than allowed by target complexity`
- [x] `References no more constraints than allowed by target complexity`
- [x] `Can be completed without hidden prerequisite work`
- [x] `Done criteria are objectively verifiable`

## 9. Agent Escape Hatch

```yaml
blocker_report:
  wp_id: WP-001
  constraint_document: ""
  section: ""
  problem_type: ambiguous
  quote: ""
  needs_from_human: ""
  proposed_resolution: ""
```

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-29` | `OpenAI Codex` | `Initial example` |
