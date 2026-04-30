# Governed AI Execution System (AOS/CDD v2)

Governed AI Execution System is an open-source governed AI execution architecture for software delivery.

Open-source reference implementation of a six-layer governed AI execution architecture where requests pass through policy, HITL approval, bounded execution, dry-run, rollback visibility, and audit before side effects are allowed.

It combines:

- `AOS/CDD`: a repository-native framework for bounded AI-assisted software work
- `agent_control_stack`: an interpretation, policy, approval, and dispatch runtime
- `platform/`: a reference hosted product layer that shows how the system can be operated through a web UI and API

The core principle is:

`The LLM is not the controller. The LLM is the bounded executor inside a governed system.`

## Project Status

Current status:

- architecture complete for the v1 test-phase model
- open-source reference implementation available in this repository
- suitable for evaluation, pilot use, extension, and self-hosted experimentation

Known limitation:

- platform policy edits are versioned and audited, but are not yet automatically written back into connected repo policy artifacts

## What This Repository Is

This repository is an open-source reference implementation of a six-layer governed AI execution architecture.

It is not just:

- a prompt pattern
- a spec-only repo
- a simple coding agent wrapper

It is a system that moves a request through:

1. product UI
2. platform/project state
3. interpretation/control
4. human approval
5. governed execution planning
6. bounded execution and audit

before any meaningful side effects are allowed.

## Why It Exists

Most AI coding systems let the model decide too much too early.

That creates predictable failure modes:

- ambiguous requests get executed instead of clarified
- unsafe or high-risk actions are not gated properly
- scope drifts across sessions
- repo changes happen without stable constraints
- failures are hard to audit after the fact

AOS/CDD v2 inverts that design.

Governance is the product.
The model is the last step.

## Architecture

The full system is built as six layers plus four control-completing components.

### Layer 1: Product UI

The user-facing surface.

It is responsible for:

- creating projects
- connecting repos
- editing policy posture
- submitting governed requests
- reviewing approvals
- reviewing run history and failures
- reviewing policy history and audit data

It does not classify requests or execute tools.

Reference implementation:

- [platform/web](./platform/web)

### Layer 2: Platform / Project State

The product backend and state layer.

It is responsible for:

- users and auth
- projects
- repo connection metadata
- request records
- approvals
- policy profiles
- run history
- single-request lock state

It manages state and forwards requests to the control layer.
It does not decide request meaning.

Reference implementation:

- [platform/api](./platform/api)

### Layer 3: Interpretation / Control

The gatekeeper.

It is responsible for:

- context restoration
- normalization / balancing
- case classification
- policy application
- approval-artifact policy overlays
- decision outcomes:
  - `clarify`
  - `refuse`
  - `dispatch`
  - `escalate`

Nothing should reach governed execution without passing through this layer.

Reference implementation:

- [agent_control_stack/pipeline.py](./agent_control_stack/pipeline.py)
- [agent_control_stack/policy.py](./agent_control_stack/policy.py)
- [agent_control_stack/runtime/case_registry.yaml](./agent_control_stack/runtime/case_registry.yaml)

### HITL Gate

The human-in-the-loop approval checkpoint between classification and execution.

Dispatchable requests pause here.
Humans can:

- approve
- reject
- escalate

This is a state machine and audit record, not an AI decision.

Reference implementation:

- governed request lifecycle in [platform/api/app](./platform/api/app)
- approval queue UI in [platform/web](./platform/web)

### Layer 4: Governed Execution

The bounded execution planning layer.

It is responsible for:

- selecting the governed procedure
- loading work packages, sessions, constraints, and artifacts
- applying repo-root path safety
- preparing dry-run-aware write declarations
- defining exactly what execution is allowed to do

It decides bounds.
It does not itself decide policy.

Reference implementation:

- [agent_control_stack/executor.py](./agent_control_stack/executor.py)
  - `GovernedExecutionPlanner`

### Layer 5: Agent / Tool Execution

The last-mile executor.

It is responsible for:

- carrying out only declared operations
- honoring dry-run mode
- producing completion evidence
- surfacing failures with traceability

This is where model- or tool-like action belongs.
It is intentionally downstream of all governance.

Reference implementation:

- [agent_control_stack/executor.py](./agent_control_stack/executor.py)
  - `GovernedExecutor`

### Layer 6: Audit / Ops

The audit and operational visibility layer.

It is responsible for:

- request records
- decision traces
- execution records
- policy context capture
- approvals
- failure traces
- retention
- CI validation
- machine-readable reports

Audit is first-class, not an afterthought.

Reference implementation:

- [agent_control_stack/store.py](./agent_control_stack/store.py)
- [agent_control_stack/ops_report.py](./agent_control_stack/ops_report.py)
- [agent_control_stack/eval.py](./agent_control_stack/eval.py)
- [agent_control_stack/policy_gate.py](./agent_control_stack/policy_gate.py)
- [.github/workflows/aos-validate.yml](./.github/workflows/aos-validate.yml)

## The Four V1 Control Components

These complete the v1 architecture.

### 1. HITL Gate

Every `dispatch` request enters a human approval checkpoint before Layer 4 execution.

Implemented behavior includes:

- `PENDING_APPROVAL`
- `APPROVED`
- `REJECTED`
- `TERMINATED`
- `ESCALATED`
- `PENDING_REVIEW`
- approval TTL expiry
- human approval queue in the UI

### 2. Rollback Path

V1 does not attempt automatic recovery.
It emphasizes clarity and observability.

Implemented behavior includes:

- `EXECUTION_FAILED -> FAILED`
- failure summary
- traceback capture
- partial artifact capture
- tool call log capture
- resubmit path

Non-goals still hold:

- no auto-retry
- no auto-revert
- no compensation logic

### 3. Dry-Run Mode

Dry-run executes the full governed path without committing writes.

Implemented behavior includes:

- UI dry-run toggle
- `mode = DRY_RUN` propagation
- explicit declared writes
- skipped write log
- fail-safe default behavior for side effects

### 4. Policy Feedback Loop

Policy evolves through human review, not autonomous adaptation.

Implemented behavior includes:

- policy profile editing in the platform
- required change reason
- version history
- previous/new state capture
- author and timestamp capture
- audit data available for review

Current limitation:

- platform policy edits are versioned and audited, but not yet automatically written back into connected repo artifacts

## AOS/CDD Framework Layer

The original repository-native framework remains a major part of the system.

Core artifacts include:

- `Vision`
- `Constraints`
- `Work Package`
- `Session Loader`
- `Vault Health`
- `CCR`
- `Completion Evidence`

Key directories:

- [spec/](./spec/)
- [_templates/](./_templates/)
- [machine/](./machine/)
- [tools/](./tools/)
- [quickstart/](./quickstart/)
- [examples/](./examples/)

## What The System Can Do Now

The current open-source reference system can:

- interpret a software-delivery request
- classify it into a governed case
- apply policy and approval context
- return `clarify`, `refuse`, `dispatch`, or `escalate`
- route approved work into governed AOS/CDD procedures
- pause dispatch at HITL
- run dry-run execution
- capture structured failure traces
- persist runs and request history
- report ops/audit summaries
- enforce policy-aware CI checks

Supported case families include:

- `new_project.initial_definition`
- `implementation.create_first_wp`
- `implementation.run_wp`
- `implementation.review_wp`
- `implementation.create_followup_wp`
- `change.constraint_conflict`
- `docs.update_constraints`
- `ops.run_validation`
- `security.protected_resource_change`

## Repository Structure

- `spec/`: framework specification
- `_templates/`: reusable AOS/CDD templates
- `machine/`: machine-readable schemas
- `tools/`: validation and framework tooling
- `examples/`: worked example projects and governed artifacts
- `agent_control_stack/`: interpretation, policy, execution, eval, reporting runtime
- `platform/`: reference hosted product layer
- `tests/`: runtime, platform, service, scenario, and regression tests
- `docs/`: architecture, API, deployment, compatibility, release guidance

## How It Works End To End

Typical flow:

1. A user creates or opens a project.
2. The user connects a repo and project context.
3. The user submits a governed request.
4. Layer 3 classifies the request and applies policy.
5. If dispatchable, the request pauses in HITL.
6. A human approves, rejects, or escalates it.
7. If approved, Layer 4 prepares the governed execution bounds.
8. Layer 5 executes only within those bounds.
9. Layer 6 records the full outcome and returns it to the UI.

## Open Source Boundary

This repository is intentionally open source as an end-to-end reference implementation.

That includes:

- the framework
- the runtime
- the reference platform
- the tests
- the docs

The intended commercial boundary, if you build a hosted business around it, is not the architecture itself.
It is the operated service around it:

- production infrastructure
- managed auth integrations
- multi-tenant operations
- hosted reliability
- billing and support

## Getting Started

### Core runtime

Install from the repo root:

```powershell
python -m pip install -e .
```

Try a governed request:

```powershell
python -m agent_control_stack.cli --text "Run WP-001 now" --context examples\agent-control-stack\runtime\run-wp-context.yaml --execute --persist
```

### Platform API

```powershell
python -m uvicorn platform.api.app.main:app --reload
```

### Platform web app

```powershell
cd platform\web
npm install
npm run dev
```

## Validation

Framework validation:

```powershell
python tools\aos_validate.py validate
python tools\aos_validate.py health-report
```

Tests:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Eval:

```powershell
python -m agent_control_stack.eval
python -m agent_control_stack.policy_gate --eval-report reports\agent-control-eval.json
```

Ops report:

```powershell
python -m agent_control_stack.ops_report --store-dir runs
```

## Current Verification State

At the current reviewed state:

- Python test suite passes
- scenario eval passes
- policy gate passes
- Next.js production build passes
- machine-readable artifact validation passes

## Documentation

- Quickstart: [QUICKSTART.md](./QUICKSTART.md)
- API: [docs/api.md](./docs/api.md)
- Architecture: [docs/architecture.md](./docs/architecture.md)
- Compatibility: [docs/compatibility.md](./docs/compatibility.md)
- Deployment: [docs/deployment.md](./docs/deployment.md)
- Release checklist: [docs/release-checklist.md](./docs/release-checklist.md)
- First release note: [docs/releases/v1.0.0-test-phase.md](./docs/releases/v1.0.0-test-phase.md)
- Platform workspace: [platform/README.md](./platform/README.md)

## Versioning

The repository currently identifies the framework as `2.0.0`.

Compatibility rules are documented in:

- [docs/compatibility.md](./docs/compatibility.md)

## License

MIT. See [LICENSE](./LICENSE).
