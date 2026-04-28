# Section 11: Failure Mode Prevention Playbook

The framework is only worth adopting if its main failure modes are handled as operational risks instead of postmortem observations. v2 addresses each known failure mode with a prevention protocol, an early warning signal, and a recovery path.

## Failure Mode 1: Vault Abandonment After Sprint One

Root cause analysis:

Teams abandon the vault when the first version is too heavy, when the vault is not connected to the actual workflow, or when no one owns health and updates. The problem is usually not lack of discipline. It is that the framework was introduced as a parallel system with no immediate payoff.

Prevention protocol:

1. Start at the lowest viable tier.
2. Tie every active AI session to a real WP or Tier 1 equivalent.
3. Require completion reports and health checks before calling the framework “in use.”
4. Assign one owner role for weekly hygiene.
5. Block or warn on stale core constraints so neglect becomes visible.

Early warning signals:

- `last validated` dates stop moving
- WPs reference outdated or nonexistent constraints
- agents stop citing constraints in completion reports
- the team says “we’ll update the vault later”

Recovery protocol:

1. Freeze new scope expansion.
2. Identify one service or domain to recover first.
3. Regenerate schema and API constraints from current implementation.
4. Mark everything else explicitly stale instead of pretending it is current.
5. Restart with Tier 1 or Tier 2 only for the recovered area.

## Failure Mode 2: Ceremonial or Shallow Documentation

Root cause analysis:

Teams fill templates to satisfy process rather than to constrain execution. The documents repeat obvious facts, omit hard boundaries, and contain no validation signal.

Prevention protocol:

1. Require every constraint to include protected fields, exclusions, and operational rules.
2. Pair narrative artifacts with machine-readable or directly referential sources where possible.
3. Run health reviews that ask whether the document changes execution decisions.
4. Reject documents that cannot answer “what is forbidden?” or “what breaks if this is wrong?”

Quality signal:

A good constraint document has three properties:

- it names the source of truth
- it rules specific agent behavior in or out
- it can be contradicted by implementation and therefore validated

Correction protocol:

1. Mark ceremonial docs yellow.
2. Rewrite only the parts that affect execution in the next two weeks.
3. Add machine-readable backing or explicit source references.
4. Delete unused narrative that no WP ever references.

## Failure Mode 3: WP Size Miscalibration

Root cause analysis:

Teams confuse planning units with execution units. They either write one huge WP per feature or fragment work into meaningless file-based micro-tasks.

Prevention protocol:

1. Apply the complexity table before a WP is marked ready.
2. Enforce the pre-execution review checklist.
3. Split any WP that crosses more than one main verification boundary.
4. Track actual completion time and use it to recalibrate future WP sizing.

Detection method:

- repeated WPs exceeding the expected time range
- WPs that require mid-flight scope edits
- WPs with vague done criteria because the scope is too broad
- WPs with no meaningful independent value because the scope is too narrow

Correction protocol:

1. Stop executing oversized WPs after the current checkpoint.
2. Split the remaining scope into new WPs.
3. Mark the original WP as superseded or partial.
4. Feed the observed size mistake into the next weekly calibration review.

## Failure Mode 4: Constraint Lag

Root cause analysis:

Implementation moves faster than documentation when constraints are updated manually after merge or not at all. The lag is amplified when schema and API changes are allowed without health enforcement.

Prevention protocol:

1. Require schema and API changes to ship with updated constraints in the same PR whenever possible.
2. Run post-merge health generation and scheduled age alerts.
3. Treat phantom constraints and undeclared names as warnings first, then blockers.
4. Require CCRs for intentional deferred alignment.

Detection:

- automated drift checks from Section 4B
- red or yellow health states
- recurring blocker reports citing outdated constraints

Recovery protocol:

1. Stop new execution against the red constraint.
2. Regenerate the machine-readable source from code or migrations.
3. Reconcile the narrative companion document.
4. Revalidate referencing WPs before resuming execution.

## Failure Mode 5: Adoption Without Prerequisite Maturity

Root cause analysis:

Teams adopt the framework because they want better AI output, but they do not yet have the engineering hygiene needed to maintain execution constraints.

### Prerequisite Maturity Checklist

The minimum bar for Tier 2 or higher is:

- code review exists and is used
- a ticket or issue system exists
- CI runs on every merge path
- the team can identify owners for schema, API, and security
- the team can write and review tests for changed behavior

If a team fails this checklist, Tier 2 and Tier 3 will be net negative.

What to do instead:

1. Use Tier 1 only.
2. Limit constraints to the highest-risk surfaces.
3. Improve basic review and CI discipline first.
4. Reassess readiness after two to four weeks of stable fundamentals.
