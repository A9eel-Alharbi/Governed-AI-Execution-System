# Section 8: Agent Escape Hatch and Feedback Protocol

Agents must surface bad constraints instead of silently compensating for them. The framework only works if ambiguity, contradiction, and staleness become visible. v2 therefore requires structured blocker and conflict reporting and defines explicit stop conditions.

## 8A. Agent Blocker Report Format

The blocker report is emitted before implementation when the agent cannot proceed safely under the loaded constraints.

```yaml
blocker_report:
  wp_id: "WP-034"
  constraint_document: "constraints/openapi.yaml"
  section: "paths./v1/subscriptions.post"
  problem_type: "ambiguous"
  problematic_quote: "status may be active or trialing depending on business policy"
  why_it_blocks_execution: "The response contract is not deterministic enough to implement tests."
  needs_from_human: "State whether create returns trialing by default or active when payment method exists."
  proposed_resolution: "Document one default status rule in the API contract and mark alternate transitions in a follow-up WP."
```

Problem types are restricted to:

- `ambiguous`
- `contradictory`
- `missing`
- `outdated`

The agent may propose a resolution, but it may not implement the resolution unless the permission model and human approval allow it.

## 8B. Constraint Conflict Report Format

When two loaded constraints disagree, the agent emits a conflict report and stops unless documented precedence already resolves the issue.

```yaml
constraint_conflict_report:
  wp_id: "WP-041"
  document_a:
    name: "constraints/schema.md"
    section: "subscriptions table"
    quote: "plan_code is the canonical plan identifier"
  document_b:
    name: "constraints/openapi.yaml"
    section: "components.schemas.Subscription"
    quote: "planId"
  contradiction_type: "field naming mismatch"
  agent_precedence_assessment:
    recommended_precedence: "schema.md"
    reasoning: "The schema is marked high-stability and the API contract appears stale relative to the migration history."
  recommended_resolution: "Raise CCR to rename API field or align schema and contract via transitional mapping."
```

### Precedence Rule

There is no universal document precedence. Precedence must be inferred from:

1. Explicit WP permission model
2. Stability class
3. Health dashboard status
4. Approved CCRs

If these do not resolve the conflict clearly, the agent stops.

## 8C. Escalation Protocol

The agent must stop execution entirely and require human intervention under these conditions:

1. A constraint conflict exists with no clear resolution.
2. The WP requires touching an out-of-scope area to be technically feasible.
3. Done criteria cannot be met without modifying a loaded constraint.
4. A security rule blocks the requested functional implementation.
5. A required constraint document is missing or red in the health dashboard.
6. A hard dependency WP is not done.

### Human Action Required

| Escalation Case | Human Must Do | Resume Condition |
|---|---|---|
| Unresolved conflict | Decide precedence or approve CCR | Updated constraint or approved CCR is merged and health dashboard is no longer blocking |
| Out-of-scope feasibility issue | Re-scope current WP or create dependency WP | WP is rewritten with explicit scope and dependencies |
| Done criteria require constraint change | Approve or reject CCR | Approved CCR merged or WP revised to current constraints |
| Security rule blocks implementation | Choose security-preserving alternative or explicitly reject the feature request | Security owner signs off on revised path |
| Missing or red constraint | Restore, validate, or replace the constraint | Health dashboard turns green or approved yellow override exists |
| Dependency not done | Complete or supersede dependency | Dependency status becomes done or WP is re-sequenced |

Resume rule:

- The agent does not resume from memory alone. It resumes only after a refreshed session loader is generated or the WP is revalidated explicitly.

## 8D. Agent Permission Model

The permission model exists to prevent both silent drift and useless rigidity.

| Permission | Agent May Do | Agent May Not Do | Typical Use |
|---|---|---|---|
| `READ-ONLY` | Implement strictly to the loaded constraint | Deviate, append proposals as part of execution, or reinterpret missing details creatively | High-stability schema, auth rules, security policy |
| `ADVISORY` | Implement to the constraint and append a structured improvement note | Change the constraint or code against an assumed improvement | Mature but imperfect docs where small quality feedback is useful |
| `PROPOSE` | Draft a CCR or blocker report describing the needed change | Implement the change before approval | API or schema areas in flux where human approval is required |
| `IMPLEMENT WITH REVIEW` | Make a narrow, local deviation and disclose it in the completion report | Make unbounded or hidden changes, or modify high-stability constraints silently | Low-stability, non-public contracts or fast-moving internal surfaces |

### Permission Selection Rules

- Default to `READ-ONLY` for high-stability constraints.
- Use `PROPOSE` when the team expects change but still wants approval control.
- Use `IMPLEMENT WITH REVIEW` only on low-stability constraints and only when the WP explicitly allows it.
- `ADVISORY` is for mature teams that want agent feedback without pausing flow.

### Structured Improvement Note for Advisory Mode

```yaml
improvement_note:
  wp_id: "WP-051"
  document: "constraints/testing-strategy.md"
  section: "coverage thresholds"
  observation: "Current threshold omits async jobs even though the repository has three production job modules."
  recommendation: "Add explicit coverage and observability criteria for async jobs."
```

The work package template must declare the permission level for every loaded document. Missing permission declarations are a validation failure.
