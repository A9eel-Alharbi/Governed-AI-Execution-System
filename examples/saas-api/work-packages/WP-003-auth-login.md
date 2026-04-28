# Work Package WP-003

## Document Control

- WP ID: `WP-003`
- Title: `Implement credential login and JWT issuance`
- Owner: `Security Lead`
- Last validated: `2026-04-28`
- Parent ticket: `GH-103`
- Status: `ready`

## 1. Dependencies

- Depends on: `none`
- Blocked by: `none`

## 2. Stability Classification

- Referenced constraint stability: `high`

## 3. In Scope

- Implement `POST /v1/auth/login`
- Verify credentials against `users`
- Issue signed JWT access token and refresh token response
- Add auth tests for success and failure paths

## 4. Out of Scope

- No password reset
- No SSO
- No refresh token persistence redesign
- No tenant membership management

## 5. Constraint Documents To Load

| Document | Sections | Permission |
|---|---|---|
| `constraints/openapi.yaml` | `POST /v1/auth/login` | `READ-ONLY` |
| `constraints/security-rules.md` | `Canonical Authentication Method, Secrets Management, Forbidden Patterns` | `READ-ONLY` |
| `constraints/schema.md` | `users table` | `READ-ONLY` |

## 6. Done Criteria

- Contract conformance: login request and response match OpenAPI and return documented 401 failure schema on invalid credentials.
- Security: password verification uses stored hash only; tokens are signed using approved secret source; no token or password value is logged.
- Test coverage: tests cover valid login, invalid password, unknown user, and malformed request payload.
- Observability: login success and failure metrics or structured logs exist without leaking sensitive fields.
- Human review: security owner reviews token issuance path before done.

## 7. Complexity

- Estimated complexity: `S`

## 8. WP Size Validation

- [x] Touches one concern, not an entire feature slice
- [x] Touches no more files than allowed by target complexity
- [x] References no more constraints than allowed by target complexity
- [x] Can be completed without hidden prerequisite work
- [x] Done criteria are objectively verifiable

## 9. Agent Escape Hatch

```yaml
blocker_report:
  wp_id: WP-003
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
