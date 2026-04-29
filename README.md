# AOS/CDD v2

AOS/CDD v2 is a repository-native framework for AI-assisted software delivery.

`AOS` stands for `Agent Operating System`.
`CDD` stands for `Constraint-Driven Development`.

It exists to solve a specific engineering problem: AI coding sessions are fast, but they drift. Models forget context, invent unstated assumptions, change more than requested, and leave weak audit trails. AOS/CDD v2 turns that into a governed execution model with explicit constraints, bounded work packages, machine-readable session context, health checks, and completion evidence.

## Choose Your Starting Point

- `Tier 1: Constraint Core`
  Use this if you are solo, early-stage, testing the framework, or want the lowest-friction path. Start in [quickstart/README.md](./quickstart/README.md).
- `Tier 2: Full Execution Discipline`
  Use this if you want bounded AI execution with work packages, session loaders, done criteria, and completion reports. Start in [spec/03-tiered-adoption.md](./spec/03-tiered-adoption.md) and [_templates/](./_templates/).
- `Tier 3: Integrated Operations`
  Use this only after Tier 2 is already working in a real repo and you want CI/CD, validator-driven enforcement, and workflow integration. Start in [spec/09-tooling-integration.md](./spec/09-tooling-integration.md).

If you are unsure, start with `Tier 1`.

## What This Is

This repository is not an application and not a runtime SDK.

It is an operating framework for teams that want AI coding work to be:

- bounded
- repeatable
- reviewable
- auditable
- recoverable when constraints change

## What It Contains

- `spec/`: canonical framework specification
- `_templates/`: reusable artifacts for real projects
- `machine/`: schemas for machine-readable operational files
- `tools/`: reference validator and enforcement helpers
- `examples/`: worked example project using the framework
- `quickstart/`: minimum viable Tier 1 adoption path
- `.github/workflows/`: baseline CI validation workflow

## Start Here

- New to the framework: [docs/START-HERE.md](./docs/START-HERE.md)
- Want the lightest entry path: [quickstart/README.md](./quickstart/README.md)
- Want the full model: [spec/00-index.md](./spec/00-index.md)
- Want to see a real example: [spec/14-worked-example.md](./spec/14-worked-example.md)

## Core Ideas

The framework is built around a small set of operational artifacts:

- `Vision`: what the product is and is not
- `Constraints`: the rules the agent must obey
- `Work Package (WP)`: the exact bounded task the agent may execute
- `Session Loader`: machine-readable runtime context for one session
- `Vault Health`: whether the constraint documents are safe to trust
- `CCR`: formal change request for constraint changes
- `Completion Report`: what the agent changed and whether it actually satisfied the WP

## Adoption Tiers

- `Tier 1`: Constraint Core
  Use this for solo builders, small experiments, or first adoption.
- `Tier 2`: Full Execution Discipline
  Use this when teams want bounded AI execution with WPs and session loaders.
- `Tier 3`: Integrated Operations
  Use this when CI, code review, and tracker integration need to enforce the model.

Read [spec/03-tiered-adoption.md](./spec/03-tiered-adoption.md) for the full tier model.

## Quick Validation

Run these from the repository root:

```powershell
python tools\aos_validate.py validate
python tools\aos_validate.py health-report
```

The validator checks machine-readable artifacts against the repository schemas and emits a `reports/vault-health-report.json` file.

## Agent Control Stack

This repository now also contains a production-oriented example implementation of a governed interpretation and dispatch layer under `agent_control_stack/`.

It is paired with the AOS/CDD example project in [examples/agent-control-stack](./examples/agent-control-stack/README.md) and demonstrates a narrow end-to-end flow:

- restore
- balance
- classify
- dispatch
- governed AOS/CDD handoff

Example:

```powershell
python -m agent_control_stack.cli --text "Run WP-001 now" --context examples\agent-control-stack\runtime\run-wp-context.yaml --execute --persist
```

That command produces:

- a structured decision envelope
- a governed execution result
- persisted run artifacts under `runs/`

The repository also includes:

- unit tests
- HTTP service tests
- scenario-level end-to-end tests under `tests/scenarios/`
- an eval runner via `python -m agent_control_stack.eval`
- a policy-aware CI gate via `python -m agent_control_stack.policy_gate`
- a persisted-run report via `python -m agent_control_stack.ops_report`
- a run-retention maintenance command via `python -m agent_control_stack.run_maintenance`

The current production-hardening path now also includes a governed policy artifact:

- `examples/agent-control-stack/ops/policy-profile.yaml`
- `examples/agent-control-stack/ops/security-threat-model.md`
- `examples/agent-control-stack/ops/APR-001-security-validation.yaml`

CI now emits machine-readable operational artifacts under `reports/` for:

- vault health
- scenario eval summary
- policy gate result
- persisted run report

The package also exposes a minimal HTTP API:

```powershell
python -m agent_control_stack.service --port 8000
```

Primary endpoints:

- `POST /interpret`
- `POST /execute`
- `GET /runs/{id}`

Full API details: [docs/api.md](./docs/api.md)

Quickstart for the current runtime: [QUICKSTART.md](./QUICKSTART.md)

Architecture overview: [docs/architecture.md](./docs/architecture.md)

Compatibility policy: [docs/compatibility.md](./docs/compatibility.md)

Deployment guide: [docs/deployment.md](./docs/deployment.md)

Release checklist: [docs/release-checklist.md](./docs/release-checklist.md)

## Try It Quickly

Install from the repository root:

```powershell
python -m pip install -e .
```

Run the main governed example:

```powershell
python -m agent_control_stack.cli --text "Run WP-001 now" --context examples\agent-control-stack\runtime\run-wp-context.yaml --execute --persist
```

That will:

- interpret the request
- apply policy and registered-case checks
- dispatch into a governed AOS/CDD procedure
- persist run artifacts under `runs/`

## Worked Example

The example project under [examples/saas-api](./examples/saas-api/) demonstrates:

- product vision
- schema and API constraints
- five work packages
- session loader and completion report
- breaking constraint change propagation
- failure-path artifacts such as blocker reports and blocked sessions

## Versioning

The current framework version is `2.0.0`.

Machine-readable artifacts include `spec_version`.

Compatibility policy:

- patch releases may add clarifications and non-breaking tooling improvements
- minor releases may add optional fields
- changes that make optional machine-readable fields required must increment the minor version and include migration guidance

See [docs/compatibility.md](./docs/compatibility.md) for the fuller contract.

## Who Should Use This

Use AOS/CDD v2 if:

- you use AI repeatedly on the same codebase
- you need continuity across sessions or tools
- you care about architectural consistency
- you need auditable implementation boundaries

Do not start with the full framework if:

- the project is a disposable prototype
- the team has no CI or review discipline
- no one owns schema, API, or security decisions

Read [spec/15-boundaries.md](./spec/15-boundaries.md) before broad adoption.

## Open Source Project Status

This repository is ready for public evaluation and pilot use. It includes:

- full framework spec
- reusable templates
- validator-backed machine-readable artifacts
- reference CI workflow
- worked example
- Tier 1 quickstart path
- governed interpretation and dispatch runtime
- policy-aware CI gate
- scenario eval and ops reporting surfaces

It is suitable for evaluation, pilot adoption, extension, and use as the starting point for a governed AI-development workflow.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT. See [LICENSE](./LICENSE).
