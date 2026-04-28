# AOS/CDD v2

AOS/CDD v2 is a repository-native framework for AI-assisted software delivery.

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

This repository is a release candidate for public use. It includes:

- full framework spec
- reusable templates
- validator-backed machine-readable artifacts
- reference CI workflow
- worked example
- Tier 1 quickstart path

It is suitable for evaluation, pilot adoption, and extension.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT. See [LICENSE](./LICENSE).
