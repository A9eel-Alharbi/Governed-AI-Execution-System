# Work Package WP-001

## Document Control

- WP ID: `WP-001`
- Title: `Add subscriptions and usage reporting core schema`
- Owner: `Backend Lead`
- Last validated: `2026-04-28`
- Parent ticket: `GH-101`
- Status: `ready`

## 1. Dependencies

- Depends on: `none`
- Blocked by: `none`

## 2. Stability Classification

- Referenced constraint stability: `high`

## 3. In Scope

- Add `subscriptions`, `usage_events`, and `usage_reports` tables exactly as specified in the schema constraint.
- Add declared indexes and foreign keys.
- Add migration verification test or equivalent integration check.

## 4. Out of Scope

- No API handlers
- No auth changes
- No billing provider synchronization logic
- No UI work

## 5. Constraint Documents To Load

| Document | Sections | Permission |
|---|---|---|
| `constraints/schema.md` | `subscriptions, usage_events, usage_reports tables` | `READ-ONLY` |
| `constraints/vision.md` | `In Scope, Architecture Direction Decisions` | `ADVISORY` |
| `constraints/security-rules.md` | `PII inventory, Forbidden Patterns` | `READ-ONLY` |

## 6. Done Criteria

- Schema conformance: migration creates only the three declared tables and their documented indexes and foreign keys.
- Schema conformance: no protected field in existing tables is renamed or removed.
- Test coverage: migration verification proves the tables and indexes exist in a disposable test database.
- Security: no plaintext credential or PII handling is introduced in migration logic or test fixtures.
- Human review: backend owner reviews migration file and confirms no undeclared schema side effects.

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
| `2026-04-28` | `OpenAI Codex` | `Initial example` |
