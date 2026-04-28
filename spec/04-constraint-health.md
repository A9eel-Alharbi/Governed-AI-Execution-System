# Section 4: Constraint Health and Staleness System

Constraint health is a first-class operating concern in AOS/CDD v2. A constraint that exists but no longer matches implementation is not neutral documentation. It is a source of incorrect execution. v2 therefore treats health state as executable metadata and blocks work when critical artifacts are stale.

## 4A. Staleness Classification Rules

Staleness is determined by both age and triggering events. Age-only systems miss major drift after high-change merges. Event-only systems miss documents that nobody re-validated after slow silent drift. v2 uses both.

### Staleness Thresholds by Document Type

| Document Type | Triggers | Green | Yellow | Red | Re-validation Owner | Re-validation Action |
|---|---|---|---|---|---|---|
| Vision | Age and major scope/event trigger | Validated within 30 days and no major product boundary change | 31 to 60 days old or one unresolved major product change | Over 60 days old or directly contradicted by approved roadmap change | Product lead | Review scope, target users, out-of-scope, unanswered questions, and architecture decisions against current roadmap. Update or reaffirm in change log. |
| Schema constraint | Age and migration/event trigger | Validated within 7 days and matches migration history | 8 to 14 days old or migration landed with no constraint validation yet | Over 14 days old, migration mismatch, or phantom table/column detected | Backend lead or data owner | Compare canonical DDL reference to actual migration chain, confirm table inventory, relationships, indexes, protected fields, and audit rules. Update `last validated` and health dashboard. |
| API contract | Age and deployment/event trigger | Validated within 7 days and OpenAPI diff clean | 8 to 14 days old or endpoint changed in code but contract not revalidated | Over 14 days old, deployed schema mismatch, or undocumented endpoint/field detected | API owner | Run OpenAPI diff against current service schema, review error schemas, auth declarations, and field behavior rules. Update contract and dashboard. |
| Testing strategy | Age and CI/event trigger | Validated within 30 days and CI gates align | 31 to 45 days old or new module type lacks testing policy | Over 45 days old or CI gates diverge from document | Engineering lead | Check coverage thresholds, required suites, mutation policy, and forbidden patterns against actual CI and recent PRs. |
| Security rules | Age and security/event trigger | Validated within 30 days and no auth/PII policy drift | 31 to 45 days old or security-sensitive change landed without explicit review | Over 45 days old, auth model drift detected, or PII handling mismatch found | Security owner | Review auth flow, RBAC or ABAC rules, PII inventory, secrets management, and OWASP controls against implementation and incident learnings. |
| Work package | Age and dependency/event trigger | Ready or in-progress with validated dependencies and green constraints | 8+ days in draft, or a referenced constraint turns yellow | Referenced constraint red, dependency invalid, or scope contradicted by CCR | WP owner | Recheck scope, dependencies, permission levels, and done criteria against current constraints and open CCRs. |

### Operational Rules

- A red constraint cannot be used for new WP execution.
- A yellow constraint may be used only if the WP explicitly acknowledges the risk and the owner accepts manual review before completion.
- Any event-triggered mismatch sets at least yellow immediately, regardless of age.
- Any proven contradiction between implementation and constraint sets red immediately.

## 4B. Automated Staleness Detection

After every merge to the protected main branch, CI runs a `vault-health` job that produces a machine-readable report and updates the vault dashboard. The report is an operational artifact, not a build log summary.

### Automated Checks

| Check | Tool / Technique | Failure Signal | Pipeline Action | Notification Target |
|---|---|---|---|---|
| Schema constraint vs migration history | Parse canonical migration reference plus migration directory hash; compare declared table and column inventory to current migration state | Missing table, missing column, extra undocumented table, extra undocumented column, index mismatch | `block` if mismatch in governed tables; `warn` if non-governed experimental area only | Backend lead, WP owner if affected |
| API contract vs service schema | Generate or fetch current OpenAPI from service, run OpenAPI diff against canonical contract | Breaking diff, undocumented endpoint, undocumented response field, missing error schema | `block` for breaking or undocumented public surface; `warn` for additive internal-only endpoints not yet exposed | API owner, service owner |
| Undeclared names in codebase | Static scan using rule files derived from constraint inventories; compare table names, endpoint paths, entity names, protected field names | Names in code absent from any constraint file | `warn` first two runs; `block` after grace period in Tier 3 | Domain owner, PR author |
| Phantom constraints | Compare names declared in constraint files to code, migrations, and generated OpenAPI | Constraint declares table, field, or endpoint not present in implementation | `warn` for deprecated items with retirement marker; `block` for undeclared phantom active items | Constraint owner |

### Output Format

The job emits:

1. A detailed report file, for example `aos/health/vault-health-report.json`
2. An updated `vault-health.yaml`
3. Optional PR or issue comments for newly opened red conditions

Minimum report shape:

```json
{
  "generated_at": "2026-04-28T10:00:00Z",
  "checks": [
    {
      "document_id": "schema-core",
      "status": "red",
      "check": "schema-migration-diff",
      "finding": "Column subscriptions.plan_code renamed in migration but not in constraint document",
      "action": "block"
    }
  ]
}
```

## 4C. Manual Validation Protocol

Not all constraints can be verified mechanically. v2 handles that directly instead of pretending prose can be fully automated.

### Review Cadence

| Document Type | Cadence | Review Format | Sign-Off Mechanism | Validated Means |
|---|---|---|---|---|
| Vision | Monthly or before major initiative | Checklist review in pull request or planning session | Product lead approval in change log | Scope, target users, architecture decisions, and exclusions still match active roadmap |
| Testing strategy | Monthly | Checklist against CI configuration and recent exceptions | Engineering lead sign-off | Thresholds, suites, and forbidden patterns still match actual practice |
| Security rules | Monthly and after auth or PII changes | Checklist plus targeted implementation spot-check | Security owner sign-off | Auth flow, authorization logic, PII inventory, and secrets handling match implementation reality |

### Manual Review Checklist Rules

Manual reviews must use fixed checklists. Open-ended “looks good” review does not count as validation.

Required checklist items:

- Does the artifact still match current implementation and operating policy?
- Did any related merges, incidents, or roadmap changes occur since last validation?
- Are the exclusions still deliberate, or are they missing scope?
- Does the change log explain the current state well enough for a new engineer or agent?

If any answer is no, the artifact remains yellow or red until corrected.

## 4D. Constraint Retirement Protocol

Retiring a constraint is mandatory when implementation is removed. Leaving old constraints in place creates phantom authority.

Retirement steps:

1. Mark the artifact section as `deprecated` with a retirement date and replacement or removal note.
2. Merge the implementation removal or endpoint decommission change.
3. Run automated phantom detection. If the retired item still exists in code, the retirement cannot complete.
4. Update referencing work packages. Future WPs must not load retired sections.
5. Remove the retired section from active inventories after the agreed retention window.
6. Update `vault-health.yaml` and close or open any associated CCR entries.

Rules:

- A deprecated constraint may remain for history during the retention window, but it must not appear active.
- Deprecated constraints must be excluded from undeclared-name checks only if explicitly tagged as retired.
- If a table or endpoint is removed without retiring its constraint, the health job sets the document red.
