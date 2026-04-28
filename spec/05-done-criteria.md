# Section 5: Work Package Done Criteria System

Done criteria in AOS/CDD v2 are a contract, not a courtesy note. A WP is not complete because code exists or because a tool reported green. It is complete only when its declared behavioral, constraint, and verification obligations are satisfied.

## 5A. Done Criteria Taxonomy

Every WP must declare done criteria using the categories below. Omitted categories are allowed only when explicitly marked not applicable with a reason.

| Criterion Type | Required When | Minimum Requirement |
|---|---|---|
| Schema conformance | Any WP that creates, alters, reads, or depends on governed data structures | Changed persistence behavior matches schema constraint and migration source of truth. No undeclared columns, indexes, or relationship changes. |
| Contract conformance | Any WP touching API endpoints, event payloads, or inter-service schemas | Request and response shapes match the declared machine-readable contract. All documented status codes and error schemas are exercised. |
| Test coverage | All WPs | Unit or equivalent behavioral tests for introduced logic plus the highest-value integration check for the changed boundary. New code coverage must not fall below module floor. |
| Security criteria | WPs touching auth, authorization, PII, secrets, external input, or external connectivity | Inputs validated, auth rules enforced, sensitive data handled per security constraint, and forbidden patterns absent. |
| Performance criteria | Required for list endpoints, fan-out jobs, indexing changes, high-volume pipelines, or any WP with expected load impact | Measured or benchmarked result stays within declared target or justified threshold. |
| Observability criteria | Required for async jobs, integrations, background processing, and production incident-prone paths | Logs, metrics, and failure signals exist at the points needed for diagnosis and alerting. |
| Human review criteria | Required when permission model is `PROPOSE` or `IMPLEMENT WITH REVIEW`, when constraints are yellow, or when public API/schema changes occur | Named reviewer confirms scope, deviations, and evidence before WP status changes to done. |

## 5B. Done Criteria Templates by WP Type

These templates are meant to be copied into work packages and then specialized. They are written to be objectively checkable by a junior engineer or by automation where possible.

### CRUD Endpoint: Single Resource

- Schema conformance: endpoint reads and writes only the tables named in the WP; no undeclared persistence side effects.
- Contract conformance: request schema matches OpenAPI for all required, optional, nullable, read-only, and write-once fields; `2xx`, `4xx`, and auth failure responses match documented schemas.
- Test coverage: unit tests cover validation and service branching for the endpoint module; integration tests verify success, validation failure, auth failure, and not-found or conflict path as applicable.
- Security: tenant boundary is enforced; no response leaks foreign-tenant data; external input is validated before persistence.
- Performance: P95 latency benchmark under target for one-resource create/read/update/delete flow if endpoint is public.
- Human review: reviewer confirms changed files align with WP in-scope and OpenAPI diff is expected.

### Database Migration: Additive

- Schema conformance: migration only adds declared tables, columns, indexes, or constraints; no existing column semantics are weakened.
- Contract conformance: dependent APIs and jobs remain valid or are updated in the same WP if explicitly scoped.
- Test coverage: migration test or integration verification proves the new structure exists and can be used by the intended code path.
- Security: new PII-bearing fields are added to the PII inventory and inherit encryption or logging rules.
- Performance: new indexes are justified against expected query shape.
- Human review: backend owner reviews migration rollback safety and locking risk.

### Database Migration: Breaking

- Schema conformance: breaking change matches approved CCR and includes explicit backward-compatibility or cutover steps.
- Contract conformance: all affected API and job contracts are updated or blocked by dependency WPs.
- Test coverage: migration-up and migration-down or compensating recovery path is tested where technically supported; affected reads and writes are validated.
- Security: no policy regression in protected fields or audit requirements.
- Performance: migration plan documents lock duration or data backfill impact.
- Human review: required before execution and before marking done.

### Authentication Feature

- Contract conformance: token request and response schemas match contract; all documented auth failure responses are implemented.
- Test coverage: tests cover success, expired token, invalid signature, revoked token, and refresh rotation failure path.
- Security: token storage, hashing, TTLs, and secret usage match security rules; no sensitive values are logged.
- Observability: auth failures and token rotation events emit diagnostic metrics or structured logs.
- Human review: security owner or delegated reviewer signs off.

### Authorization Rule Change

- Contract conformance: endpoint behavior changes are documented where status codes or access outcomes differ.
- Test coverage: permission matrix tests cover each affected role and tenant-scoping case.
- Security: deny-by-default behavior preserved; no broadened access without explicit approval.
- Human review: reviewer checks role matrix against security rules and CCR if applicable.

### Background / Async Job

- Schema conformance: job touches only declared tables and queues.
- Contract conformance: input and output payload shapes to queues or APIs match documented contracts.
- Test coverage: unit tests cover scheduling logic and idempotency decisions; integration test covers one successful run and one failure/retry path.
- Performance: runtime and batch size are measured or bounded; job does not exceed declared load target.
- Observability: job emits start, success, failure, retry, and dead-letter signals.

### Third-Party API Integration

- Contract conformance: outbound request and inbound response mapping are documented and tested against representative fixtures.
- Test coverage: tests cover success, timeout, rate limit, invalid payload, and provider 5xx handling.
- Security: secrets come only from approved secret sources; provider data with PII is classified and redacted in logs.
- Observability: correlation IDs and provider response codes are logged structurally.
- Human review: reviewer verifies retry policy and failure isolation.

### Data Transformation Pipeline

- Schema conformance: source and destination schemas are declared; no hidden field creation or dropping.
- Test coverage: fixture-based transformation tests cover nominal, null, malformed, and duplicate records.
- Performance: throughput target or batch ceiling stated and verified.
- Observability: row counts, failure counts, and rejected-record reasons are emitted.

### UI Component With API Dependency

- Contract conformance: component uses only documented API fields and handles loading, empty, validation, unauthorized, and error states.
- Test coverage: component tests cover render states and event handling; integration or contract-mock test verifies shape assumptions.
- Security: no privileged fields are exposed in the UI if not allowed by the role model.
- Human review: reviewer checks that UI assumptions do not exceed API contract.

### CI/CD Pipeline Change

- Contract conformance: pipeline inputs and outputs match expected repository conventions.
- Test coverage: pipeline change is exercised with dry run, reusable workflow test, or equivalent validation.
- Security: secrets scope is least-privilege; no plaintext secret output.
- Observability: failures are visible with actionable logs and artifact outputs.
- Human review: infra owner confirms merge gate effects and rollback path.

### Security Rule Implementation

- Schema or contract conformance: changes align exactly with security rules or approved CCR.
- Test coverage: tests prove both allowed and denied behavior at the relevant boundary.
- Security: implementation closes the named risk without introducing weaker fallback behavior.
- Observability: security-relevant denials or failures are logged without leaking sensitive data.
- Human review: mandatory security sign-off.

## 5C. Done Criteria Anti-Patterns

| Weak Criteria | Why It Fails | Rewritten Version |
|---|---|---|
| `Tests pass` | Does not state which tests or what behavior is covered | `Unit tests cover all new public service methods. Integration test verifies successful create flow and duplicate create rejection against seeded test database.` |
| `Implements endpoint` | Says nothing about contract or failure paths | `Endpoint matches OpenAPI request and response schemas for 201, 400, 401, and 409 responses, with examples validated by tests.` |
| `Database updated` | Hides whether the schema is additive, breaking, or compliant | `Migration adds subscriptions.cancel_at column only, preserves existing indexes, and does not alter any protected fields.` |
| `Auth works` | Non-specific and not threat-aware | `Access token issuance, expiration, revocation, and refresh rotation are covered by tests; invalid token returns documented 401 schema.` |
| `Handles errors` | Fails to name error classes | `Provider timeout, 429, malformed payload, and 5xx responses each trigger documented retry or fail-fast behavior with tests.` |
| `No regressions` | Not measurable | `Changed module coverage remains above 80% and existing subscription CRUD integration suite stays green.` |
| `Performance is acceptable` | No target or measurement | `Batch job processes 10,000 records in under 90 seconds in staging fixture benchmark.` |
| `Logging added` | Says nothing about usefulness or safety | `Job emits structured start, success, retry, and failure logs with tenant_id and correlation_id, but never raw tokens or email values.` |
| `UI completed` | Omits contract and state handling | `Component renders loading, empty, success, unauthorized, and server-error states using only documented API fields.` |
| `CI updated` | Does not define validation behavior | `New pre-merge job blocks on OpenAPI breaking diff and uploads vault-health report artifact on every main merge.` |

## 5D. Agent Self-Check Protocol

Before declaring any WP done, the agent must emit a structured completion report. If the report is missing, the WP remains incomplete even if the code is correct.

Required report shape:

```yaml
session_id: "session-021"
wp_id: "WP-021"
status: "complete"
files_created:
  - path: "services/api/tests/test_subscriptions_create.py"
    purpose: "Integration coverage for create endpoint"
files_modified:
  - path: "services/api/subscriptions/service.py"
    reason: "Implements create workflow and conflict handling"
tests_written:
  - name: "test_create_subscription_success"
    type: "integration"
    verifies: "201 response persists subscription and returns documented payload"
constraints_consulted:
  - document: "constraints/schema.md"
    sections: ["subscriptions table", "audit column rules"]
constraint_conflicts: []
done_criteria_status:
  - criterion: "contract conformance"
    status: "pass"
    evidence: "Responses 201/400/401/409 covered by tests"
blockers: []
```

Rules:

- `status` is `complete`, `partial`, or `blocked`.
- Every done criterion from the WP must appear in `done_criteria_status`.
- Any unresolved blocker forces `status` to `partial` or `blocked`.
- Any deviation under `IMPLEMENT WITH REVIEW` must appear in `constraint_conflicts` or an equivalent deviation entry.
