# Work Package WP-002

## Document Control

- WP ID: `WP-002`
- Title: `Implement create and fetch subscription endpoints`
- Owner: `API Lead`
- Last validated: `2026-04-28`
- Parent ticket: `GH-102`
- Status: `ready`

## 1. Dependencies

- Depends on: `WP-001`
- Blocked by: `none`

## 2. Stability Classification

- Referenced constraint stability: `mixed`

## 3. In Scope

- Implement `POST /v1/subscriptions`
- Implement `GET /v1/subscriptions/{subscriptionId}`
- Persist and retrieve subscription rows according to contract and schema
- Add unit and integration tests for success and error paths

## 4. Out of Scope

- No billing provider API synchronization
- No subscription update or cancel endpoint
- No UI consumer changes
- No schema changes

## 5. Constraint Documents To Load

| Document | Sections | Permission |
|---|---|---|
| `constraints/schema.md` | `subscriptions table, index strategy` | `READ-ONLY` |
| `constraints/openapi.yaml` | `POST /v1/subscriptions, GET /v1/subscriptions/{subscriptionId}` | `READ-ONLY` |
| `constraints/vision.md` | `In Scope, Non-Functional Requirements` | `ADVISORY` |
| `constraints/security-rules.md` | `Authorization model, Forbidden Patterns` | `READ-ONLY` |

## 6. Done Criteria

- Contract conformance: request and response payloads for both endpoints match OpenAPI exactly for 201, 200, 400, 401, 403, 404, and 409 behaviors where applicable.
- Schema conformance: handlers read and write only the `subscriptions` table and do not introduce undeclared persistence side effects.
- Test coverage: unit tests cover validation and service branching; integration tests verify create success, duplicate conflict, auth failure, tenant authorization failure, and fetch not-found.
- Security: only `billing_admin` and `tenant_admin` may create subscriptions; foreign-tenant fetch must not disclose existence details beyond documented response behavior.
- Performance: create and fetch operations remain within the public endpoint latency target under staging fixture load.
- Human review: reviewer confirms changed files match WP scope and no undeclared endpoint fields appear.

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
  wp_id: WP-002
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
