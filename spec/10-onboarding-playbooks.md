# Section 10: Onboarding and Adoption Playbook

Adoption fails when the framework is introduced at the wrong depth for the team’s operating reality. v2 avoids that by defining explicit playbooks for four common contexts. The playbooks are opinionated because weak guidance is how teams end up with ceremonial documents and abandoned vaults.

## 10A. Solo Builder / Indie Hacker Playbook

Full AOS/CDD is inappropriate for most solo builders. The correct target is Tier 1 only. The goal is not governance completeness. The goal is anti-hallucination, continuity across sessions, and prevention of accidental architectural drift.

### Minimum Viable Setup

Required artifacts:

- one vision document
- one schema constraint if the project has persistent data
- one API contract if the project exposes endpoints
- one security rules file limited to auth method, secrets handling, and forbidden patterns
- one manual vault health file

Skip entirely:

- command registry beyond a tiny local note
- formal CCR workflow unless schema or API changes are already causing confusion
- full weekly hygiene ceremony
- issue tracker sync

How to get value with low overhead:

- keep the vision under one page
- keep the schema constraint limited to canonical DDL and protected fields
- keep the API contract to the endpoints the agent is actually touching this week
- force every agent session to cite the loaded constraints before coding

Recommended time investment:

- new small project: 60 to 120 minutes
- existing messy project: 2 to 4 hours for the first useful pass

Use `quickstart/` rather than the full `_templates/` directory for this first pass. The full templates are for teams graduating beyond the minimum viable constraint set.

Common solo-builder mistakes:

1. Writing the full framework before the product exists. Avoidance: stop at Tier 1.
2. Documenting every idea instead of the volatile edges that confuse agents. Avoidance: constrain only schema, contract, auth, and out-of-scope boundaries.
3. Never updating the vault after the first sprint. Avoidance: refresh the health file every time schema or API changes.

## 10B. Small Team Playbook

Target context: 2 to 6 people, Tier 2.

Vault ownership belongs to a role, not a person. The correct role is usually the tech lead or staff engineer closest to the architecture boundary. That owner does not write every artifact, but they enforce consistency, resolve conflicts, and keep weekly hygiene from disappearing.

Constraint document changes are reviewed by the domain owner for the artifact being changed:

- schema by backend lead or data owner
- API contract by service owner
- security rules by security owner or designated senior engineer
- testing strategy by engineering lead

Weekly vault hygiene cadence:

- 30 to 45 minutes once per week
- review yellow and red health items
- review open CCRs
- review blocked WPs caused by constraints
- retire phantom constraints or superseded WPs

Disagreements about constraint content are resolved through a bounded process:

1. State the disputed rule in one sentence.
2. State the implementation impact.
3. Decide whether the dispute is architectural or executional.
4. If architectural, resolve outside the WP and update the constraint first.
5. If executional, resolve in the WP or a CCR.

Onboarding a new developer:

1. Read the vision.
2. Read the onboarding prompt.
3. Read one real WP and its completion report.
4. Walk through the health dashboard and one recent CCR.

Onboarding a new AI tool:

The framework abstracts the tool. To switch from Claude to Cursor or another agent, keep the same onboarding prompt, session loader, completion report requirement, and permission model. The tool changes. The execution contract does not.

## 10C. Growth-Stage Team Playbook

Target context: existing codebase, 10+ engineers, Tier 2 moving toward Tier 3.

Do not attempt a big-bang retrofit. Bootstrap the vault from the highest-friction domains first:

1. public API surface
2. core schema
3. authentication and authorization
4. highest-change workflows used by AI agents

Constraint bootstrapping process for an existing codebase:

1. extract current schema from migrations or production-compatible DDL
2. generate current OpenAPI from code if possible
3. document only current reality first, not desired future cleanup
4. mark known mismatches explicitly as yellow or red instead of hiding them
5. create the first CCRs from the most dangerous mismatches

Migration plan from ad hoc prompting:

1. Choose one team and one service.
2. Require Tier 1 constraints for that service.
3. Move only high-risk work to WPs first.
4. Add health automation once the core constraints stabilize.
5. Expand only after the team is already using the current artifacts.

Training the team on constraint discipline:

- teach WP scoping before teaching templates
- teach stop conditions before teaching automation
- review both good and bad completion reports
- use the first month to calibrate document quality, not to optimize ceremony

Governance at 10+ engineer scale:

- each high-stability constraint has one named owner
- each service has one API contract owner
- one platform or enablement owner maintains automation and schemas
- no cross-team breaking constraint change merges without CCR and impact assessment

## 10D. Regulated Environment Playbook

Target context: Tier 3 with audit pressure.

Additional artifacts required:

- formal approval records for security rules and Class 3 CCRs
- retention policy for completion reports and health snapshots
- reviewer identity and timestamp on manual validations
- linkage from PR, WP, CCR, and deployment artifact

Audit evidence generation:

The vault can produce evidence for:

- who approved a constraint change
- which work package implemented it
- what tests and validations were required
- whether the constraint was healthy at time of execution

Formal sign-off protocol:

- security rules: security owner sign-off
- breaking schema or API change: domain owner plus engineering lead
- regulated data handling change: compliance or security delegate where required

Integration with compliance tooling:

- mirror CCR IDs and approval statuses into the existing ticket or audit system
- retain CI artifacts for health reports and completion reports
- ensure repository protections preserve review and merge history

What AOS/CDD v2 does not cover even here:

- legal interpretation
- policy authorship
- external auditor negotiation
- evidence retention outside the team’s actual repository and CI controls
