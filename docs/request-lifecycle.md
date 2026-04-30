# Request Lifecycle

This document explains one governed request from submission to final result.

It is the operational view of the system.

## Goal

The system exists to make sure a request is:

- understood before execution
- approved before side effects
- bounded before tools run
- auditable after completion or failure

## Happy Path

### 1. Request submission

The user submits a request from the web UI.

Main implementation:

- `platform/web`
- `platform/api/app/main.py`

The request is associated with:

- a user
- a project
- a policy profile
- a repo connection context

### 2. Layer 2 creates the request record

Before control logic matters, the platform stores a request record.

Responsibilities:

- persist request text
- attach project and user context
- set initial status
- enforce the v1 single-request lock where applicable

Main implementation:

- `platform/api/app/store.py`
- `platform/api/app/models.py`

### 3. Layer 3 restores context and interprets the request

The control layer processes the request in this order:

1. restore context
2. normalize / balance
3. classify
4. apply policy

Main implementation:

- `agent_control_stack/pipeline.py`
- `agent_control_stack/policy.py`

The output is one of four outcomes:

- `clarify`
- `refuse`
- `dispatch`
- `escalate`

### 4. If clarify

Execution stops.

The user gets a clarification response explaining what is missing or ambiguous.

Layer 4 and Layer 5 are not invoked.

### 5. If refuse

Execution stops.

The user gets a refusal reason.

Layer 4 and Layer 5 are not invoked.

### 6. If escalate

The request moves into a higher-review path.

It does not execute until that path approves it.

### 7. If dispatch

The request is eligible to move to the HITL gate.

Dispatch does not itself grant permission to execute.

## HITL Gate

The human-in-the-loop gate is the safety checkpoint between interpretation and execution.

Main implementation:

- `platform/api/app/main.py`
- `platform/web/components`

The stored approval context should include:

- original request
- policy decision
- intended actions
- project/user context
- expiry / TTL information

Human outcomes:

- `approve`
- `reject`
- `escalate`

If the request expires before approval, TTL logic handles the terminal state and lock release behavior.

## Layer 4 Planning

After approval, governed execution planning begins.

Main implementation:

- `agent_control_stack/executor.py`
- `GovernedExecutionPlanner`

Layer 4 is responsible for:

- choosing the governed procedure
- loading work-package, constraints, and session context
- checking vault / path / repo safety conditions
- constructing the target artifact path
- declaring the allowed write operations
- producing an explicit `ExecutionPlan`

Layer 4 does not execute tools.

## Layer 5 Execution

Execution begins only after planning has declared the allowed operations.

Main implementation:

- `agent_control_stack/executor.py`
- `GovernedExecutor`

Layer 5 is responsible for:

- carrying out declared operations
- respecting dry-run mode
- capturing tool-call logs
- returning completion evidence on success
- returning structured failure details on failure

## Dry-Run Path

Dry-run follows the same overall lifecycle:

1. submission
2. Layer 2 state
3. Layer 3 decision
4. HITL approval
5. Layer 4 planning
6. Layer 5 execution simulation
7. Layer 6 audit

The difference is:

- write operations are skipped
- skipped writes are logged
- the result explains what would have changed

## Failure Path

If execution fails:

- status becomes terminal
- traceback is preserved
- last successful step is preserved
- partial artifacts are preserved
- tool-call log is preserved
- the user sees failure details in the platform
- the request can be resubmitted through the supported lifecycle

The v1 rollback path is observational, not compensating.

That means:

- no auto-retry
- no auto-revert
- no automatic recovery workflow

## Layer 6 Audit

Every meaningful path must produce a usable audit trail.

Main implementation:

- `agent_control_stack/store.py`
- `agent_control_stack/ops_report.py`
- platform history/detail surfaces

Audit should preserve:

- request text
- control decision
- policy context
- approval history
- execution trace
- write or skipped-write data
- completion evidence or failure trace
- final status

## V1 Lock Behavior

The product uses a single-request project lock in v1.

Purpose:

- prevent concurrent execution-capable requests from overlapping in one project

Main implementation:

- `platform/api/app/main.py`
- `platform/api/app/store.py`
- `platform/api/app/models.py`

Expected behavior:

- lock acquired on active execution-capable work
- second request rejected while lock is active
- timeout / terminal outcomes release the lock
- manual force-unlock exists for recovery paths

## Policy Feedback Loop

Policy changes are human-authored and versioned.

The current loop is:

1. review run history and failures
2. inspect policy behavior
3. edit policy with a reason
4. store version history
5. apply the new policy to future requests

Current limitation:

- platform policy edits are not yet automatically written back into connected repo artifacts

## Related Documents

- [system-map.md](./system-map.md)
- [architecture.md](./architecture.md)
- [maintainer-guide.md](./maintainer-guide.md)
