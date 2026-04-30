# System Map

This document is the maintainer-facing map of the Governed AI Execution System.

It exists to answer four questions quickly:

1. What is this system?
2. How do the old AOS/CDD tiers relate to the current repo?
3. Which folders implement which parts?
4. What must not be broken?

## Two Views Of The Same System

There are two valid ways to describe this repository.

### 1. Three-tier product structure

This is the packaging and subsystem view:

1. `AOS/CDD`
   The repository-native framework for bounded AI-assisted software work.
2. `agent_control_stack`
   The interpretation, policy, approval, dispatch, and governed execution runtime.
3. `platform/`
   The reference product layer with web UI, API, project state, HITL, and policy management.

### 2. Six-layer execution architecture

This is the runtime control-flow view:

1. Layer 1: product UI
2. Layer 2: platform / project state
3. Layer 3: interpretation / control
4. Layer 4: governed execution planning
5. Layer 5: bounded execution
6. Layer 6: audit / ops

The system is easiest to reason about when both views are kept in mind:

- tiers describe the major subsystems
- layers describe how a request moves through the system

## Old AOS/CDD Tiers

The original repository described AOS/CDD as a maturity ladder.

- `Tier 1`: lightweight constraint-first onboarding
- `Tier 2`: work-package and session-based execution discipline
- `Tier 3`: integrated operations, validation, and automation

These tiers still matter, but they are now only one part of the broader governed execution system.

They are not the same thing as:

- the six execution layers
- `clarify / refuse / dispatch / escalate`
- HITL approval outcomes

## Core Principle

The core principle of the repository is:

`The LLM is not the controller. The LLM is the bounded executor inside a governed system.`

That principle shows up in four places:

- Layer 3 decides what the request means
- HITL decides whether execution may proceed
- Layer 4 defines the execution bounds
- Layer 5 executes only inside those bounds

## Main Runtime Flow

At a high level, one governed request moves like this:

```text
UI request
  -> Layer 2 request record
  -> Layer 3 restore / normalize / classify / policy decision
  -> clarify | refuse | dispatch | escalate
  -> if dispatch: HITL approval gate
  -> if approved: Layer 4 planning and bounds
  -> Layer 5 bounded execution
  -> Layer 6 audit, reporting, and result visibility
```

Supporting paths:

- `dry-run`: full flow, no side effects
- `rollback path`: failure capture, no auto-revert
- `single-request lock`: one active governed request per project in v1
- `policy feedback loop`: audited human edits, not autonomous policy mutation

## Folder Map

### Tier 1: `AOS/CDD`

Main folders:

- `spec/`
- `_templates/`
- `machine/`
- `tools/`
- `quickstart/`
- `examples/`

Primary role:

- provide repo-native artifacts
- define constraints and work-package discipline
- support validation and governed software delivery patterns

### Tier 2: `agent_control_stack`

Main folders and files:

- `agent_control_stack/pipeline.py`
- `agent_control_stack/policy.py`
- `agent_control_stack/executor.py`
- `agent_control_stack/store.py`
- `agent_control_stack/ops_report.py`
- `agent_control_stack/runtime/case_registry.yaml`

Primary role:

- classify requests
- apply policy
- produce governed execution plans
- enforce bounded execution
- store and report audit data

### Tier 3: `platform/`

Main folders:

- `platform/api/`
- `platform/web/`

Primary role:

- expose the reference product surface
- hold project/request/policy state
- implement HITL interactions
- display run history, policy history, and failures

## Layer-To-File Map

### Layer 1: Product UI

Main code:

- `platform/web`
- key components under `platform/web/components`

Responsibilities:

- project creation
- repo connection UI
- request submission
- approval review
- run and failure visibility
- policy editing and history display

### Layer 2: Platform / Project State

Main code:

- `platform/api/app/main.py`
- `platform/api/app/models.py`
- `platform/api/app/store.py`
- `platform/api/app/control.py`

Responsibilities:

- request records
- project state
- repo connection metadata
- policy profiles
- approvals and run history
- single-request lock state

### Layer 3: Interpretation / Control

Main code:

- `agent_control_stack/pipeline.py`
- `agent_control_stack/policy.py`
- `agent_control_stack/runtime/case_registry.yaml`

Responsibilities:

- restore context
- normalize / balance
- classify
- apply policy
- produce one of:
  - `clarify`
  - `refuse`
  - `dispatch`
  - `escalate`

### HITL Gate

Main code:

- `platform/api/app/main.py`
- `platform/web/components`

Responsibilities:

- block execution pending human decision
- support `approve`, `reject`, and `escalate`
- enforce TTL behavior
- record approval chain and status transitions

### Layer 4: Governed Execution Planning

Main code:

- `agent_control_stack/executor.py`
- `GovernedExecutionPlanner`

Responsibilities:

- select governed procedure
- resolve bounded target path
- load work-package, constraints, session, and related context
- perform vault/repo safety checks
- declare write operations
- return an execution plan

Layer 4 defines the bounds.
It must not be the thing doing the work.

### Layer 5: Bounded Execution

Main code:

- `agent_control_stack/executor.py`
- `GovernedExecutor`

Responsibilities:

- execute only declared write operations
- respect `LIVE` vs `DRY_RUN`
- capture tool-call log
- return completion evidence or structured failure data

### Layer 6: Audit / Ops

Main code:

- `agent_control_stack/store.py`
- `agent_control_stack/ops_report.py`
- `.github/workflows/aos-validate.yml`
- `platform` history/detail views

Responsibilities:

- persist execution records
- retain traces and failure evidence
- drive ops reporting
- feed policy review and operational visibility

## Control-Completing Components

These are not separate numbered layers, but they are essential to the architecture.

### Dry-run mode

- full request flow still runs
- approval is not skipped
- declared writes are logged, not executed

### Rollback path

- failures become observable and auditable
- traceback, last step, partial artifacts, and tool log are preserved
- v1 does not auto-retry, auto-revert, or auto-recover

### Single-request lock

- one active governed request per project in v1
- protects the product from overlapping execution state

### Policy feedback loop

- policy edits are human-driven
- changes are versioned and reasoned
- audit data informs future policy tuning

## Known V1 Limitation

The main documented remaining gap is:

- platform policy edits are versioned and audited, but are not yet automatically written back into connected repo policy artifacts

That limitation is tracked in the public backlog and should remain explicit in future docs.

## What Must Not Be Broken

The following invariants define the system:

1. The LLM is not the controller.
2. No request may bypass Layer 3 policy interpretation.
3. No executable path may bypass HITL when approval is required.
4. Layer 4 defines bounds; Layer 5 performs bounded execution.
5. Dry-run must not perform real writes.
6. Failure handling must preserve evidence rather than hide it.
7. Audit is part of the product, not an optional afterthought.
8. Policy mutation must remain human-controlled.

## Related Documents

- [architecture.md](./architecture.md)
- [request-lifecycle.md](./request-lifecycle.md)
- [maintainer-guide.md](./maintainer-guide.md)
- [deployment.md](./deployment.md)
