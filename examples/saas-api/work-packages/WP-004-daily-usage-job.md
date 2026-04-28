# Work Package WP-004

## Document Control

- WP ID: `WP-004`
- Title: `Implement daily usage aggregation background job`
- Owner: `Backend Lead`
- Last validated: `2026-04-28`
- Parent ticket: `GH-104`
- Status: `ready`

## 1. Dependencies

- Depends on: `WP-001`
- Blocked by: `none`

## 2. Stability Classification

- Referenced constraint stability: `mixed`

## 3. In Scope

- Aggregate `usage_events` into `usage_reports` by tenant and day
- Make job idempotent for repeat runs on the same report date
- Emit structured logs or metrics for job start, success, and failure
- Add job-focused tests

## 4. Out of Scope

- No usage event ingestion endpoint
- No provider billing export
- No real-time aggregation

## 5. Constraint Documents To Load

| Document | Sections | Permission |
|---|---|---|
| `constraints/schema.md` | `usage_events, usage_reports tables` | `READ-ONLY` |
| `constraints/testing-strategy.md` | `Performance Test Requirements, Forbidden Test Patterns` | `ADVISORY` |
| `constraints/security-rules.md` | `Forbidden Patterns` | `READ-ONLY` |

## 6. Done Criteria

- Schema conformance: job reads only `usage_events` and writes only `usage_reports`.
- Test coverage: unit tests cover grouping and idempotency logic; integration test verifies one successful aggregation and one rerun on the same day without duplicate report creation.
- Performance: job aggregates 100,000 fixture usage events for one day within the agreed staging benchmark threshold.
- Observability: job emits structured start, success, failure, and rerun/idempotent outcome signals.
- Human review: reviewer confirms the job can be re-run safely after partial failure.

## 7. Complexity

- Estimated complexity: `M`

## 8. WP Size Validation

- [x] Touches one concern, not an entire feature slice
- [x] Touches no more files than allowed by target complexity
- [x] References no more constraints than allowed by target complexity
- [x] Can be completed without hidden prerequisite work
- [x] Done criteria are objectively verifiable

## 9. Agent Escape Hatch

```yaml
blocker_report:
  wp_id: WP-004
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
| `2026-04-28` | `OpenAI Codex` | `Initial example` |
