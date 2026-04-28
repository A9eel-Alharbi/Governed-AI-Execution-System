# Section 15: What AOS/CDD v2 Does Not Cover

AOS/CDD v2 is an execution-governance framework for AI-assisted engineering work. It is not a universal operating system for software teams. Its value depends on clear boundaries.

## Team Coordination Boundary

AOS/CDD v2 does not replace Agile, Scrum, Kanban, project management, roadmap ownership, or staffing decisions. It does not decide what to build, how to prioritize work across teams, or how to manage interpersonal collaboration. It governs how a defined unit of work is executed against explicit constraints.

## Architecture Boundary

AOS/CDD v2 enforces decisions; it does not make them. A bad tenancy model, poor domain boundary, or incoherent API philosophy will still be enforced faithfully if the constraints encode it. The framework improves consistency and traceability. It does not generate sound architecture from weak technical judgment.

## Human Skill Boundary

The framework does not compensate for absent engineering fundamentals. A team that cannot review schema changes, reason about API compatibility, or recognize security regressions will not become strong merely by filling in better templates. AOS/CDD v2 reduces ambiguity. It does not replace technical literacy.

## AI Failure Boundary

The constraint model does not eliminate all AI failure classes. It does not fully prevent:

- incorrect implementation inside correctly understood constraints
- subtle logic bugs not covered by tests
- overconfident but syntactically valid completion reports
- weak human approvals of bad CCRs
- poor reasoning caused by missing repository context outside the loaded documents

It reduces hallucinated architecture and silent drift. It does not make model reasoning infallible.

## When To Set It Aside

AOS/CDD v2 should be set aside or reduced to Tier 1 when:

- the project is a prototype, spike, or hackathon with disposable code
- the architecture is intentionally exploratory and changing daily
- the team cannot maintain even a small set of accurate constraints
- no one owns review of schema, API, or security decisions
- the process cost is exceeding the value of consistency and auditability

In those contexts, direct prompting plus lightweight ADRs or plain tickets is usually the better tool.

## What To Do Before Adoption If Not Ready

If a team fails the readiness bar, it should not pretend otherwise. The right move is to improve the prerequisites first:

1. Establish basic ticket hygiene.
2. Ensure code review exists and is taken seriously.
3. Put CI on every merge path.
4. Identify actual owners for schema, API, and security decisions.
5. Start with one or two core constraints only.

If those basics are missing, Tier 2 and Tier 3 will become ceremony rather than control.

## Framework Compatibility Boundary

AOS/CDD v2 does not promise perpetual compatibility for every artifact shape without versioning. Teams must treat machine-readable artifacts as versioned contracts. The repository therefore includes `spec_version` on machine-readable artifacts so validators and migration tooling can distinguish framework generations cleanly.
