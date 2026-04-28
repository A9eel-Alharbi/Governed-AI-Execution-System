# Section 3: Tiered Adoption Model

## Design Rule

Teams must be able to extract value without committing to the full operating model on day one. Tiering is a requirement, not a convenience feature.

## Tier 1: Constraint Core

Tier 1 requires:

- One vision document
- One schema constraint artifact if the project has persisted data
- One API contract artifact if the project exposes endpoints
- One lightweight security rules document
- One machine-readable vault health dashboard, updated manually if automation does not exist

Tier 1 simplifies work packages. A team may use issue tracker tickets directly instead of full WP documents if each ticket includes in-scope, out-of-scope, referenced constraints, and done criteria.

The agent is not trusted to invent schema changes, API contract changes, auth models, or hidden side effects. The agent is trusted to implement within those boundaries and to propose missing details explicitly.

Humans must manually review:

- All changed constraints
- Any agent suggestion that modifies data model or contract shape
- Every completion report

Tier 1 provides immediate value over unstructured prompting by reducing hallucinated architecture, preserving continuity between sessions, and forcing explicit out-of-scope statements. It does not provide strong automation.

Realistic setup time with the `quickstart/` path: 1 to 2 hours for a new project; 2 to 4 hours for an existing codebase.

Graduation criteria to Tier 2:

- The team can keep core constraints current for two consecutive iterations.
- Tickets are already scoped with acceptable discipline.
- CI exists and is trusted.
- At least one human is willing to own vault hygiene weekly.

## Tier 2: Full Execution Discipline

Tier 2 adds:

- Formal work package templates
- Machine-readable session loaders
- Command registry
- Done criteria taxonomy by work type
- CCR workflow for constraint changes
- Weekly health review

Automation at Tier 2 is mixed. CI validates report presence, document schemas, and selected diffs. Manual review still handles security, testing strategy, and vision alignment.

Realistic setup time: 3 to 7 working days from Tier 1.

Prerequisites:

- Team size of 2 to 6 or a solo builder working in a stable product domain
- Reliable ticket ownership
- Code review exists
- CI runs on every merge

Graduation criteria to Tier 3:

- Work packages are sized consistently for at least one month
- CCR usage is normal, not exceptional
- Constraint drift findings are low and acted on quickly
- Team wants less manual review and more enforcement

## Tier 3: Integrated Operations

Tier 3 adds:

- Issue tracker synchronization
- Pre-merge health gates
- Automatic OpenAPI and schema diffs
- Scheduled staleness alerts
- PR linting against loaded constraints
- Auto-generated health dashboard

Required tooling:

- Version control with branch protection
- CI/CD capable of scheduled and post-merge jobs
- Machine-readable schema and OpenAPI source
- Scriptable issue tracker API

The health dashboard becomes a CI artifact and repository file. Merge blockers are based on red health states, missing completion reports, broken diff checks, and invalid session references.

Realistic setup time from Tier 2: 4 to 10 working days.

Ideal profile:

- Stable product team
- 5+ engineers
- Shared API ownership
- Compliance or uptime pressure
- AI usage across multiple contributors

## One-Page Onboarding Checklists

### Tier 1

1. Create `vision.md`, `schema`, `api`, and `security` artifacts. Estimate: 60 to 120 minutes.
   Shortcut: start from `quickstart/` if the team is new to the framework.
2. Fill only required fields; leave unanswered items explicit. Estimate: 60 to 90 minutes.
3. Create a manual `vault-health.yaml`. Estimate: 15 minutes.
4. Define a ticket template with in-scope, out-of-scope, constraints, and done criteria. Estimate: 30 minutes.
5. Require the agent to cite loaded constraints before implementation. Estimate: 10 minutes.
6. Review the first three agent completions manually and refine constraints. Estimate: 60 minutes.

### Tier 2

1. Adopt formal WP templates. Estimate: 60 minutes.
2. Add session loader files and command registry. Estimate: 45 minutes.
3. Split the backlog into XS to M work packages only. Estimate: 2 to 4 hours.
4. Add CCR template and policy. Estimate: 45 minutes.
5. Add weekly vault health review on the team calendar. Estimate: 15 minutes.
6. Require completion reports for every WP. Estimate: 30 minutes.

### Tier 3

1. Implement machine schemas and CI validators. Estimate: 4 to 8 hours.
2. Add API diff and schema diff jobs. Estimate: 4 to 8 hours.
3. Wire tracker synchronization. Estimate: 4 to 8 hours.
4. Add PR lint rule against undeclared entity names. Estimate: 2 to 4 hours.
5. Add scheduled staleness alerts and post-merge dashboard generation. Estimate: 2 to 4 hours.
6. Run a two-week stabilization period before turning warnings into blockers. Estimate: 2 weeks elapsed time.
