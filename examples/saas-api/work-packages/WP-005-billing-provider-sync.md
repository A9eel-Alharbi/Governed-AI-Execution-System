# Work Package WP-005

## Document Control

- WP ID: `WP-005`
- Title: `Integrate Stripe subscription identifier sync`
- Owner: `Integrations Lead`
- Last validated: `2026-04-28`
- Parent ticket: `GH-105`
- Status: `ready`

## 1. Dependencies

- Depends on: `WP-001`, `WP-002`
- Blocked by: `none`

## 2. Stability Classification

- Referenced constraint stability: `mixed`

## 3. In Scope

- Call Stripe to create or reconcile provider subscription after local subscription creation
- Persist `provider_subscription_id` on success
- Handle provider timeout, conflict, and transient failure cases
- Add integration tests with provider fixture or stub

## 4. Out of Scope

- No webhook ingestion
- No plan catalog synchronization
- No provider-specific pricing model changes

## 5. Constraint Documents To Load

| Document | Sections | Permission |
|---|---|---|
| `constraints/schema.md` | `subscriptions.provider_subscription_id` | `READ-ONLY` |
| `constraints/openapi.yaml` | `Subscription response schema` | `READ-ONLY` |
| `constraints/security-rules.md` | `Secrets Management, Forbidden Patterns` | `READ-ONLY` |

## 6. Done Criteria

- Contract conformance: subscription response remains valid if `providerSubscriptionId` is null before provider success and populated after synchronization where the flow requires it.
- Schema conformance: only `provider_subscription_id` and allowed audit timestamps are updated during provider sync.
- Test coverage: tests cover provider success, provider timeout, provider conflict, and provider 5xx retry or failure handling.
- Security: Stripe secret comes only from approved secret source and is never logged.
- Observability: provider request outcome, correlation identifier, and retry state are visible in structured logs.
- Human review: reviewer confirms retry policy and local consistency when provider sync fails after local record creation.

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
  wp_id: WP-005
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
