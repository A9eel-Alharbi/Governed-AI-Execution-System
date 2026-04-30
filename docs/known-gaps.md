# Known Gaps

This document records the current known gaps, v1 simplifications, and explicit non-goals of the Governed AI Execution System.

It exists so maintainers and contributors do not have to infer project maturity from scattered issues or past conversations.

## How To Read This Document

This file separates three categories:

1. `Known limitations`
   Real gaps or incomplete product behavior.
2. `V1 simplifications`
   Deliberate scope cuts that keep the reference implementation practical.
3. `Non-goals`
   Things the system explicitly does not attempt to do in this phase.

## Known Limitations

### 1. Policy writeback to repo artifacts is not automated

Platform policy edits are:

- versioned
- reasoned
- audited
- visible in the UI

But they are not yet automatically written back into connected repo policy artifacts.

Why this matters:

- repo-native governance is stronger when policy state in the platform and policy state in the repo stay synchronized
- the current implementation still leaves room for drift between UI-managed policy and repo-managed policy artifacts

Current status:

- documented in the README
- tracked in the public backlog

### 2. The reference executor is bounded, but still a v1 runtime

The executor architecture is correct in the important way:

- Layer 4 defines bounds
- Layer 5 executes inside those bounds

But the current executor is still a pragmatic governed reference runtime rather than a richer live autonomous agent runtime.

This means:

- bounded repo/tool operations are present
- stronger dynamic agent orchestration is not the point of the current implementation

### 3. Audit storage is split across product-shaped surfaces

The repository currently has more than one audit surface:

- platform request/run history
- core run-store and ops reporting artifacts

This is acceptable for the v1 reference implementation, but later maturity may favor a more unified audit backend or stronger cross-surface synchronization model.

## V1 Simplifications

These are deliberate and not defects by themselves.

### 1. Rollback is observational, not compensating

On failure, the system captures:

- traceback
- last successful step
- partial artifacts
- tool-call log

It does not currently perform:

- automatic repo revert
- compensating actions
- automatic recovery

### 2. The lock model is a single-request lock, not a queue

The v1 product model allows:

- one active governed request per project

It does not currently include:

- a multi-request scheduler
- queue prioritization
- fairness or resource arbitration logic

### 3. Dry-run is whole-request, not partial execution planning

Dry-run covers the full request path while suppressing side effects.

It does not support:

- mixed live/dry phases inside one request
- partial promotion from dry-run to live execution inside the same lifecycle

### 4. HITL is direct and explicit

The v1 HITL model is intentionally simple:

- approve
- reject
- escalate

It does not include:

- advanced approval routing trees
- weighted voting
- delegated approval policies
- automated risk-threshold approval

### 5. The platform is a reference product layer

`platform/` is a real reference product surface, but it is still meant to illustrate governed operation rather than represent every possible hosted product capability.

## Non-Goals

These are things the system explicitly should not do in this phase.

### 1. No auto-approval at HITL

The model or risk score must not silently approve execution.

### 2. No automatic policy mutation

The system must not rewrite policy by itself based on runs or outcomes.

### 3. No model control over human decisions

The model may inform execution planning and bounded execution.
It must not make or override HITL decisions.

### 4. No hidden write paths outside governed declaration

Write behavior must remain explicit and bounded.

### 5. No automatic retry or silent recovery on failure

Failures should be visible and auditable rather than hidden behind automatic retry behavior.

### 6. No direct shortcut from request intake to execution

Requests must not bypass:

- interpretation
- policy
- approval when required
- governed planning
- audit

## Relationship To The Public Issue Tracker

The public issue tracker is intentionally broader than this document.

It includes:

- feature gaps
- verification tasks
- documentation hardening
- regression coverage

This file is not a replacement for the issue tracker.
It is the concise architectural statement of current maturity and intentional boundaries.

## Related Documents

- [system-map.md](./system-map.md)
- [request-lifecycle.md](./request-lifecycle.md)
- [maintainer-guide.md](./maintainer-guide.md)
- [architecture.md](./architecture.md)
