# Work Package Template

## Document Control

- WP ID `[required, immutable]`: `WP-000`
- Title `[required]`: `[short action-oriented title]`
- Owner `[required]`: `[human owner]`
- Last validated `[required]`: `YYYY-MM-DD`
- Parent ticket `[required]`: `[Jira/Linear/GitHub issue reference]`
- Status `[required]`: `draft | ready | in-progress | blocked | done`

## 1. Dependencies `[required]`

- Depends on: `[explicit WP IDs or none]`
- Blocked by: `[explicit WP IDs or none]`

## 2. Stability Classification `[required]`

<!-- Choose high, low, or mixed based on referenced constraints. -->
- Referenced constraint stability: `high | low | mixed`

## 3. In Scope `[required]`

<!-- Implementation only. Must be concrete. -->
Example:
- `Add POST /v1/subscriptions endpoint`
- `Persist subscription row and emit audit record`

## 4. Out of Scope `[required]`

Example:
- `No webhook ingestion`
- `No billing provider sync`
- `No UI changes`

## 5. Constraint Documents To Load `[required]`

| Document | Sections | Permission |
|---|---|---|
| `constraints/schema.md` | `subscriptions table` | `READ-ONLY` |
| `constraints/api/openapi.yaml` | `POST /v1/subscriptions` | `PROPOSE` |

## 6. Done Criteria `[required]`

<!-- Use the done criteria taxonomy, not freeform prose. -->
Example:
- `Schema conformance: no column outside subscriptions and audit_logs is changed`
- `Contract conformance: request and response match OpenAPI examples`
- `Coverage: unit >= 80% for new module; integration test covers success and validation failure`

## 7. Complexity `[required]`

- Estimated complexity: `XS | S | M | L | XL`

## 8. WP Size Validation `[required]`

- [ ] `Touches one concern, not an entire feature slice`
- [ ] `Touches no more files than allowed by target complexity`
- [ ] `References no more constraints than allowed by target complexity`
- [ ] `Can be completed without hidden prerequisite work`
- [ ] `Done criteria are objectively verifiable`

## 9. Agent Escape Hatch `[required]`

<!-- The agent fills this only if it finds a blocker before implementation. -->
```yaml
blocker_report:
  wp_id: WP-000
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
| `YYYY-MM-DD` | `[name]` | `Initial draft` |
