# Section 9: Tooling Integration Specifications

AOS/CDD v2 is not useful at scale if it lives beside the delivery system instead of inside it. v2 therefore defines explicit integrations with an issue tracker, CI/CD, code review, and version control. The goal is not maximal tooling complexity. The goal is to remove parallel tracking and make drift visible in the tools the team already uses.

This section uses GitHub Issues and GitHub Actions as the reference implementation because the concepts map cleanly to Linear and Jira and the YAML examples are repository-native.

The reference repository now includes a minimal validator CLI at `tools/aos_validate.py` and a working workflow at `.github/workflows/aos-validate.yml`. Teams should treat those as the baseline implementation, not as final enterprise-grade tooling.

## 9A. Issue Tracker Integration

### Reference Model: GitHub Issues

Work packages may be created from issues, but the issue is not the WP. The issue is the planning and ownership record. The WP is the execution contract.

### Ticket to WP Field Mapping

| GitHub Issue Field | WP Field | Rule |
|---|---|---|
| Issue number | Parent epic or ticket reference | Required in every WP |
| Issue title | WP title seed | Must be refined into a scoped execution title |
| Issue body problem statement | In-scope and rationale seed | Must be translated into explicit in-scope and out-of-scope sections |
| Labels | Stability hints, domain ownership, urgency | May prefill constraint stability or owner suggestions |
| Milestone | Scheduling context | Informational only; not a WP dependency substitute |
| Assignee | WP owner | Required before execution |

### WP Status to Ticket Status Mapping

| WP Status | Issue Signal |
|---|---|
| `draft` | Issue open, label `wp:draft` |
| `ready` | Issue open, label `wp:ready` |
| `in-progress` | Issue open, label `wp:in-progress` |
| `blocked` | Issue open, label `wp:blocked` plus blocker comment |
| `done` | Issue open or closed depending on whether sibling WPs remain; label `wp:done` |

### Done Criteria Completion Trigger

When a completion report is validated and the WP status changes to `done`, automation may:

1. Post a completion summary comment on the parent issue.
2. Remove `wp:in-progress`.
3. Add `wp:done`.
4. Close the issue only if the issue maps one-to-one with the WP and no follow-up WPs remain.

### Blocker Report Comment Format

```text
[AOS/CDD Blocker] WP-034
Constraint: constraints/openapi.yaml :: paths./v1/subscriptions.post
Problem: ambiguous
Needs: choose default returned subscription status on create
Proposed resolution: document one default status rule and defer alternate transitions
```

### Constraint Health Warnings

Constraint health warnings should appear on issues as labels or comments:

- `constraint:yellow`
- `constraint:red`
- `ccr:impact-review-required`

### Adaptation to Linear or Jira

The mapping is direct:

- Issue labels become tags or custom fields.
- Completion comments remain comments.
- WP status becomes workflow state or an auxiliary field.
- Blocker reports become templated comments or linked sub-issues.

The hard requirement is bidirectional traceability, not GitHub-specific field names.

## 9B. CI/CD Integration

Tier 3 requires CI to verify the parts of the framework that can be checked mechanically. Humans remain responsible for policy judgment, but CI owns drift detection, report presence, and machine-validated artifact shape.

### Required Gates

| Gate | Purpose | Automation Scope |
|---|---|---|
| Pre-merge: constraint staleness | Detect drift and phantom constraints before merge | Fully automatable for schema/API/name checks |
| Pre-merge: done criteria auto-verification | Confirm tests, coverage, and contract checks declared by the WP are actually present where possible | Partial |
| Pre-merge: completion report presence and validity | Prevent silent merges with no execution evidence | Fully automatable |
| Post-merge: vault health dashboard update | Refresh repository-wide health status after main branch changes | Fully automatable |
| Scheduled: constraint age alerts | Surface yellow/red aging before merges fail | Fully automatable |

### Reference GitHub Actions Configuration

#### Pre-merge Constraint Health

```yaml
See `.github/workflows/aos-validate.yml` in the repository. The current reference implementation validates machine-readable artifacts and emits a `vault-health-report.json` artifact. Schema-to-code drift and OpenAPI diff should be added as a follow-up enhancement rather than implied to exist already.
```

#### Pre-merge Completion Report Validation

The current validator already checks completion-report files structurally through `machine/completion-report.schema.json`. PR-body or ticket-binding checks still need project-specific implementation.

#### Post-merge Dashboard Update

The reference CLI emits a JSON health report. Teams that want repository-updated YAML dashboards should add a project-specific generation or synchronization step on top of that baseline.

#### Scheduled Age Alerts

Scheduled age alerts are not fully implemented in the reference repository yet. The current CLI already computes age-derived flags in the generated report, which is the prerequisite for adding scheduled notifications cleanly.

Tradeoff:

- A fully blocking CI policy too early causes adoption backlash. Tier 3 should begin with warnings for one stabilization period, then turn repeated findings into blockers.

## 9C. Code Review Integration

Reviewers must compare code changes against AOS/CDD artifacts, not just against local code style.

### Required Review Checks

1. The PR description references at least one WP ID.
2. Changed files match the WP in-scope declaration.
3. Test changes correspond to the WP done criteria.
4. New entity names, table names, endpoint paths, or public fields are declared in loaded constraints.
5. Any deviation under `IMPLEMENT WITH REVIEW` is explicitly called out in the completion report.

### Automated Lint Rule

Reference lint rule:

- Build an allowlist from the loaded constraint documents named in the session loader and WP.
- Scan changed files for new table names, endpoint literals, event types, and public DTO fields.
- Fail review if new governed names appear outside the allowlist and no CCR is referenced.

This is not perfect static analysis. It is a practical drift detector.

### Reviewer Checklist

```yaml
reviewer_checklist:
  pr_references_wp: true
  changed_files_match_scope: true
  tests_match_done_criteria: true
  undeclared_names_absent_or_approved: true
  completion_report_present: true
  deviations_flagged_if_any: true
  reviewer: "team-lead"
  reviewed_at: "YYYY-MM-DD"
  notes: ""
```

## 9D. Version Control Conventions

The vault is versioned with the code because constraints without commit history are untrustworthy.

### Repository Rules

- Constraint changes may occur in feature branches when tied to a specific WP or CCR.
- Shared high-stability constraints should not be edited casually across unrelated branches; use one branch per intentional change stream when practical.
- Class 3 changes must reference a CCR in the branch name or commit series.

### Commit Message Conventions

Examples:

- `AOS: WP-034 add subscription create completion report`
- `AOS: CCR-014 rename plan_code to plan_key`
- `AOS: health refresh vault dashboard`

### Tag Strategy

Use tags for major constraint milestones that change downstream execution assumptions:

- `schema-v2`
- `api-contract-v3`
- `auth-policy-v2`

These tags do not replace Git history. They make coordinated rollback and audit navigation faster.
