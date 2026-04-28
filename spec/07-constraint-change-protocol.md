# Section 7: Constraint Change Protocol

Constraint changes are operational events. In v1, a schema or contract could change and leave multiple work packages half-valid with no formal propagation path. v2 fixes that by treating every constraint change as a classified event with impact assessment, approval, propagation, and rollback rules.

## 7A. Change Classification

v2 uses three classes because not all constraint changes create the same risk.

| Class | Trigger | Propagation Protocol | Approval | In-Flight WP Effect |
|---|---|---|---|---|
| Class 1: Additive | New table, new optional field, new endpoint, new role capability, new non-conflicting rule that does not invalidate existing behavior | Record CCR, update affected constraint, update health dashboard, notify referencing WP owners if relevant | Domain owner | No forced restart. Referencing WPs continue unless they choose to adopt the additive change. |
| Class 2: Modifying | Existing constraint changes in backward-compatible way, such as widened enum acceptance, optional response field, index strategy change, additional validation rule that does not break current clients | Record CCR, run impact assessment, flag referencing WPs for revalidation, update command registry or session loaders if affected | Domain owner plus engineering lead | In-progress WPs pause at next checkpoint until revalidated. Queued WPs cannot start until impact review marks them safe. |
| Class 3: Breaking | Renamed field, removed endpoint, auth model shift, table drop, non-backward-compatible schema or contract change | Record CCR, freeze affected WPs, run mandatory impact assessment, update dependencies and restart plan, reissue session loaders | Domain owner plus engineering lead plus affected service owner; security owner if auth or PII affected | In-progress WPs move to blocked. Partial work is reviewed, either salvaged into follow-up WPs or discarded, and execution restarts only after re-scoping. |

Classification rule:

- If there is any doubt between Class 2 and Class 3, treat it as Class 3 until impact assessment proves otherwise.

## 7B. Impact Assessment Process

Impact assessment exists to answer one question precisely: which work packages are no longer safe to execute as currently written?

### Identification Method

Affected WPs are identified using:

1. The `constraint documents to load` section in each WP.
2. Session loaders that reference the changed document section.
3. Open completion reports or blocked reports that cite the changed constraint.
4. Optional CI index of document-to-WP references generated from repository scans.

### Impact Assessment Form

```yaml
impact_assessment:
  ccr_id: "CCR-014"
  constraint_changed:
    document: "constraints/schema.md"
    section: "subscriptions.plan_code"
  change_class: "Class 3"
  affected_wps:
    - wp_id: "WP-202"
      current_state: "in-progress"
      recommended_action: "stop and re-scope"
      estimated_rework_cost_hours: 4
    - wp_id: "WP-203"
      current_state: "ready"
      recommended_action: "update dependency and regenerate session loader"
      estimated_rework_cost_hours: 1
  assessment_owner: "backend-lead"
  approved_by:
    - "engineering-lead"
  approved_at: "YYYY-MM-DD"
```

### Approval Rule

No implementation proceeds on the changed constraint until the assessment is approved. For Class 1, approval can be lightweight. For Class 2 and Class 3, approval must be explicit and recorded.

## 7C. In-Flight WP Handling

### Class 1

No forced action is required. The CCR is logged, the health dashboard is updated, and affected WP owners are informed. A current WP may ignore the additive change unless it now depends on it.

### Class 2

Protocol:

1. Mark all referencing in-progress WPs as `review-required`.
2. Prevent queued referencing WPs from starting until revalidation is complete.
3. Compare current WP scope and done criteria to the updated constraint.
4. If the WP remains valid, update `last validated`, session loader references if needed, and resume.
5. If the WP now needs extra scope, split the extra work into a new WP rather than silently expanding the old one.

Partial work handling:

- Code already written may remain if it still conforms after revalidation.
- Tests that encoded old assumptions must be updated before the WP can resume.

### Class 3

Protocol:

1. Move all affected in-progress WPs to `blocked`.
2. Stop agents immediately on next preflight or checkpoint.
3. Review partial code and determine one of three actions:
   - `salvage`: keep reusable internal code and create a new WP to complete against the new constraint
   - `dual-path`: temporarily support old and new constraint through a transitional WP sequence
   - `discard`: abandon incompatible partial work and close the WP as superseded
4. Rewrite or replace the affected WPs with new in-scope, out-of-scope, dependencies, and done criteria.
5. Generate new session loaders before any agent resumes work.

Hard rule:

- A Class 3 change may not be resolved by editing the original WP in place without leaving an audit trail. Supersede it or log an explicit revision entry.

## 7D. Constraint Rollback Protocol

Constraint documents are version-controlled with the application code. Rollback means reverting both the constraint change and any implementation that depended on it, or issuing a corrective follow-up if direct revert is unsafe.

Rollback steps:

1. Identify the CCR to roll back and the commits that implemented it.
2. Revert the constraint artifact change in version control or apply a corrective commit that restores prior semantics.
3. Re-run impact assessment against all WPs created or modified after the CCR.
4. Mark affected WPs as:
   - `resume-original` if the old constraint is valid again
   - `superseded` if replacement work exists
   - `blocked` if implementation state is now mixed
5. Regenerate the vault health dashboard and any session loaders referencing the rolled-back sections.
6. Add a rollback entry to the CCR and to the affected constraint change log.

Versioning rules:

- Constraints are changed in feature branches when tied to a WP or CCR, but Class 3 changes require a dedicated branch or a clearly isolated change set within the feature branch.
- The merge commit or squash commit message must reference the CCR ID.
- Major breaking constraint milestones should be tagged, for example `schema-v3` or `auth-policy-v2`.
