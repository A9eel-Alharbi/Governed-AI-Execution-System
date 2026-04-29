# Start Here

This repository supports three adoption tiers. They are real and they map to different parts of the repo. If you do not choose a tier first, the repository looks more complicated than it actually is.

The short version:

- `Tier 1` is the lowest-friction path and starts in `quickstart/`
- `Tier 2` is the full execution model and starts by reading a few spec docs, then instantiating `_templates/`
- `Tier 3` is the baseline integration and validation layer and starts only after Tier 2 is already useful in a real project

If you are unsure, start with `Tier 1`.

## What This Repository Is

This repository is the source-of-truth framework repo for AOS/CDD.

It is not an application and not a runtime SDK. Its job is to provide:

- the framework specification
- reusable templates
- machine-readable schemas
- validation tooling
- a worked example
- a low-friction first-adoption path

Most teams will not work “inside” this repository forever. They will learn from it, copy or adapt its artifacts, and integrate AOS/CDD into their own software repository.

## Pick Your Tier

## Tier 1: Constraint Core

Choose Tier 1 if you are:

- a solo builder
- testing the framework for the first time
- working on an early-stage or low-maturity project
- trying to keep process overhead low

### What Tier 1 Actually Uses

Use:

- [quickstart/README.md](../quickstart/README.md)
- `quickstart/vision.md`
- `quickstart/schema.md`
- `quickstart/api-contract.md`
- `quickstart/security-rules.md`
- `quickstart/vault-health.yaml`

Optionally use:

- [tools/aos_validate.py](../tools/aos_validate.py) for validation

### What Tier 1 Does Not Require

Tier 1 does not require:

- the full work package library
- full session-loader discipline
- CCR workflows for every change
- command registry
- failure-path artifact library
- CI integration

### What You Are Doing In Tier 1

You are defining the minimum viable source of truth for the project before letting the agent code against it.

This means:

1. define product purpose and boundaries
2. define schema source of truth
3. define API source of truth
4. define basic security rules
5. track health manually

Then you let the agent work against those constraints.

## Tier 2: Full Execution Discipline

Choose Tier 2 if you want:

- bounded AI execution
- explicit work scoping
- session-level context loading
- done criteria enforcement
- completion reports
- formal constraint-change handling

### What Tier 2 Actually Uses

Read first:

- [spec/03-tiered-adoption.md](../spec/03-tiered-adoption.md)
- [spec/13-agent-onboarding-prompt.md](../spec/13-agent-onboarding-prompt.md)
- optionally [spec/14-worked-example.md](../spec/14-worked-example.md)

Then instantiate and use:

- [_templates/constraints/](../_templates/constraints/)
- [_templates/work-packages/](../_templates/work-packages/)
- [_templates/ops/](../_templates/ops/)
- [machine/](../machine/)
- [tools/aos_validate.py](../tools/aos_validate.py)

### Important Distinction

`spec/` is not the operational artifact set for Tier 2.

`spec/` tells you how the framework works.

The actual Tier 2 artifact set is:

- `_templates/`
- `machine/`
- `tools/`
- your project-specific constraints, work packages, sessions, health files, and completion reports

### What You Are Doing In Tier 2

You are turning AI work into bounded execution units.

That means:

1. define or refine project constraints
2. create a Work Package for one bounded task
3. create a Session Loader for one execution session
4. execute only that WP
5. require a Completion Report
6. use CCRs when constraints change materially

## Tier 3: Integrated Operations

Choose Tier 3 only after Tier 2 is already working in a real project.

Tier 3 is for teams that want:

- validator-backed CI checks
- health reporting in automation
- repository workflow integration
- stronger operational enforcement

### What Tier 3 Actually Uses

Read first:

- [spec/09-tooling-integration.md](../spec/09-tooling-integration.md)

Use:

- [tools/aos_validate.py](../tools/aos_validate.py)
- [.github/workflows/aos-validate.yml](../.github/workflows/aos-validate.yml)
- `machine/` schemas
- project-specific health, session, CCR, and completion-report artifacts

### What Tier 3 Is Today

Tier 3 is real in this repository, but it is a baseline implementation.

It currently provides:

- working structural validation
- a working reference CI workflow
- machine-readable health reporting
- session/WP consistency checks

It does not yet provide:

- one-command installation
- deep semantic validation of every governed surface
- exhaustive product-specific integrations

So Tier 3 should be understood as:

- a valid advanced operating mode
- useful for pilot adoption
- not yet a fully mature “enterprise governance platform”

## Which Path Should You Choose?

Choose `Tier 1` if:

- you are starting from an empty project
- you want to test whether the framework helps at all
- you want low friction

Choose `Tier 2` if:

- you already see value in the constraints
- you want the full WP/session/completion-report discipline
- you expect multiple AI sessions on the same repo

Choose `Tier 3` if:

- Tier 2 is already working
- the project has CI discipline
- you want to automate health and artifact validation

## Best Reading Order

If you want the shortest useful path:

1. [README.md](../README.md)
2. [quickstart/README.md](../quickstart/README.md)
3. [spec/13-agent-onboarding-prompt.md](../spec/13-agent-onboarding-prompt.md)
4. [spec/14-worked-example.md](../spec/14-worked-example.md)

If you want the full framework:

1. [spec/01-architecture.md](../spec/01-architecture.md)
2. [spec/03-tiered-adoption.md](../spec/03-tiered-adoption.md)
3. [spec/05-done-criteria.md](../spec/05-done-criteria.md)
4. [spec/07-constraint-change-protocol.md](../spec/07-constraint-change-protocol.md)
5. [spec/13-agent-onboarding-prompt.md](../spec/13-agent-onboarding-prompt.md)
6. [spec/14-worked-example.md](../spec/14-worked-example.md)

## Worked Example

The worked example is under [examples/saas-api/](../examples/saas-api/).

Use it when you want to see:

- what a populated constraint set looks like
- what a good WP looks like
- what a session loader looks like
- what a completion report looks like
- how a breaking CCR propagates
- what a blocked/failure path looks like

Do not treat `examples/` as the default starting point for your own project. It is a reference implementation, not the minimal onboarding path.

## Validation

From the repository root, run:

```powershell
python tools\aos_validate.py validate
python tools\aos_validate.py health-report
```

The validator checks the machine-readable artifacts it knows about and emits `reports/vault-health-report.json`.

## What This Repo Does Not Do

It does not replace product management, engineering judgment, or architecture decision-making. It governs execution against explicit constraints; it does not invent good constraints by itself.

Read [spec/15-boundaries.md](../spec/15-boundaries.md) before broad adoption.

## personal notes
What i personaly do when i first clone this repo is run this prompt in the agent chat:
This repository is using AOS/CDD (Agent Operating System / Constraint-Driven Development).

  For this project, do not start by writing application code.

  Your first job is to help me define the project using the framework already present in this repository.

  Work in this order:
  1. quickstart/vision.md
  2. quickstart/schema.md
  3. quickstart/api-contract.md
  4. quickstart/security-rules.md
  5. quickstart/vault-health.yaml

  For now, we are in artifact-definition mode, not implementation mode.

  Do not invent extra features.
  Do not write production code yet.
  Keep the scope minimal and explicit.
  When drafting, help me define only what is necessary for the first version of the project.
  After the quickstart files are defined, we will create the first Work Package and session loader.

  ## Why this matters

  Without this, the agent may:

  - start coding immediately
  - skip constraints
  - add features you did not ask for
  - ignore the framework structure you just cloned

  So yes, the first step is basically:
  teach the agent how this repo is supposed to be used.
