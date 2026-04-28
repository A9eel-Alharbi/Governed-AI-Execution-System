# Section 6: Work Package Calibration Guide

Work package calibration is a control surface, not a taste preference. Oversized WPs hide risk and encourage scope creep. Tiny WPs create ceremony and break architectural coherence. AOS/CDD v2 defines explicit sizing, splitting, and sequencing rules so teams can tell when a WP is malformed before an agent executes it.

## 6A. Complexity Scale Definition

The complexity scale is based on elapsed implementation effort for a prepared engineer or capable agent operating with valid constraints, not on calendar time or ticket size mythology.

| Size | Typical Time | Max Files Touched | Max Constraint Docs Referenced | Max Tables Modified | Split Rule |
|---|---|---|---|---|---|
| XS | 0.5 to 2 hours | 3 | 2 | 0 | Split if it touches more than one boundary or needs more than one test type |
| S | 2 to 6 hours | 6 | 3 | 1 | Split if it includes both schema and public API change |
| M | 6 to 12 hours | 10 | 4 | 2 | Split if it requires multiple deploy-order assumptions or more than one domain concern |
| L | 12 to 24 hours | 15 | 5 | 3 | Usually split before execution; only acceptable with explicit owner approval |
| XL | Over 24 hours | Over 15 | Over 5 | Over 3 | Must be split. Execution is forbidden as a single WP. |

Operational rule:

- Tier 2 should target XS to M only.
- Tier 3 may allow rare L WPs for coordinated infrastructure or migration work, but never XL.

## 6B. WP Splitting Rules

Split a WP when any of the following is true:

1. It changes both a stable constraint and a low-stability consumer in one step without a declared cutover.
2. It requires more than one human approval role to finish.
3. It modifies more tables, files, or constraints than the selected complexity band allows.
4. It includes work that can be merged independently with preserved value.
5. It contains more than one primary verification boundary, such as schema plus auth plus UI.
6. The done criteria cannot fit on one review screen without collapsing into vague language.

### Split Examples

Bad WP:

- `Add subscriptions table, create CRUD endpoints, wire billing provider sync, and expose admin page`

Correct split:

1. `WP-101`: additive schema migration for subscriptions table
2. `WP-102`: POST and GET subscription API endpoints against the new schema
3. `WP-103`: billing provider synchronization worker
4. `WP-104`: admin UI component for subscription state

Bad WP:

- `Rename plan_code everywhere`

Correct split if breaking:

1. `WP-201`: add new column or compatibility alias behind approved CCR
2. `WP-202`: update write path to dual-write or write new field
3. `WP-203`: update reads and API contract
4. `WP-204`: remove deprecated field in follow-up breaking cleanup

### Anti-Patterns

`One WP per file` is wrong because files are implementation containers, not behavior boundaries. A single coherent behavior may require changes across route, service, test, and contract files and still be one good WP.

`One WP per epic` is wrong because epics are planning containers, not execution atoms. An epic often mixes schema, contract, UI, testing, and rollout concerns that must be split to preserve reviewability and rollback safety.

## 6C. WP Sequencing Rules

Dependency types:

- `Hard dependency`: the current WP cannot start until the predecessor is done.
- `Soft recommendation`: the predecessor improves efficiency or reduces rework, but the current WP can still proceed.

Rules:

1. Hard dependencies must be declared whenever a WP depends on a missing schema object, contract change, secret, queue, or approved CCR.
2. Circular hard dependencies are forbidden. If detected, the owner must extract the shared prerequisite into a new upstream WP.
3. WPs may run in parallel only when they do not modify the same high-stability constraint section and do not rely on each other’s unmerged code.
4. If two WPs reference the same constraint document and one modifies it through an approved CCR, the other WP must be revalidated before execution continues.
5. A WP queued behind a Class 3 breaking CCR is automatically moved to blocked until impact review completes.

### Circular Dependency Resolution

When `WP-A` depends on `WP-B` and `WP-B` depends on `WP-A`, the owner must:

1. Identify the actual prerequisite both need.
2. Create `WP-0X` for that prerequisite.
3. Repoint both WPs to depend on `WP-0X`.
4. Re-scope both WPs so each can complete independently after `WP-0X`.

## 6D. WP Review Checklist

Humans complete this checklist before issuing a command that starts execution. The agent should refuse execution if any item fails.

```yaml
wp_review_checklist:
  wp_id: "WP-000"
  scoped_correctly: true
  complexity_band_valid: true
  referenced_constraints_green: true
  hard_dependencies_done: true
  done_criteria_specific_and_verifiable: true
  permission_levels_explicit_for_all_constraints: true
  ccr_impact_checked_if_needed: true
  reviewer: "engineering-lead"
  reviewed_at: "YYYY-MM-DD"
  notes: ""
```

Interpretation rules:

- `scoped_correctly` is false if the WP spans multiple independent concerns or is too trivial to justify a separate execution cycle.
- `referenced_constraints_green` may be overridden only by explicit owner sign-off and only for yellow, never red.
- `ccr_impact_checked_if_needed` is required whenever the WP touches a constraint under active change.
