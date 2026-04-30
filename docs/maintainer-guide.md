# Maintainer Guide

This document is for people changing the architecture, control logic, or platform behavior.

Its purpose is to make regressions harder.

## What This Repository Is

This repository is:

- an open-source reference implementation
- a governed AI execution architecture
- a product-shaped reference system, not just a framework sketch

The system is built from:

- `AOS/CDD`
- `agent_control_stack`
- `platform/`

## What Future Maintainers Must Understand

Before changing anything important, a maintainer should understand:

1. the three-tier structure
2. the six-layer runtime flow
3. HITL as a real execution gate
4. Layer 4 vs Layer 5 separation
5. dry-run as an enforced write discipline
6. audit as a first-class product requirement

If any of those ideas are unclear, start with:

- [system-map.md](./system-map.md)
- [request-lifecycle.md](./request-lifecycle.md)
- [architecture.md](./architecture.md)

## Architecture Invariants

These are not style preferences. They are design constraints.

### 1. The model is not the controller

The model may help execute bounded work.
It must not be allowed to decide ungoverned execution scope.

### 2. Layer 3 decides meaning before execution exists

Requests must pass through interpretation and policy before planning or execution.

### 3. HITL is a real block, not a cosmetic status

If approval is required, Layer 4 and Layer 5 must not proceed until approval exists.

### 4. Layer 4 plans; Layer 5 executes

Do not merge these responsibilities back together.

Layer 4 should:

- select procedure
- load constraints
- declare writes
- define bounds

Layer 5 should:

- carry out declared operations
- respect dry-run
- produce evidence

### 5. Dry-run must stay inverted

The safe default is:

- no write unless explicitly declared and allowed

Do not introduce tools or code paths that can silently mutate state outside that discipline.

### 6. Failure evidence matters

A failure path is not complete unless it preserves:

- traceback
- last successful step
- partial artifacts
- tool-call log

### 7. Audit is part of the product

If a new path is added and Layer 6 cannot explain what happened, the path is incomplete.

### 8. Human policy control must remain explicit

Policy feedback is human-driven.

Do not add:

- autonomous policy mutation
- model-driven approval decisions
- hidden policy overlays that are not visible in audit history

## Important Files

### Control and execution

- `agent_control_stack/pipeline.py`
- `agent_control_stack/policy.py`
- `agent_control_stack/executor.py`
- `agent_control_stack/runtime/case_registry.yaml`

### Audit and ops

- `agent_control_stack/store.py`
- `agent_control_stack/ops_report.py`
- `.github/workflows/aos-validate.yml`

### Platform API

- `platform/api/app/main.py`
- `platform/api/app/control.py`
- `platform/api/app/models.py`
- `platform/api/app/store.py`

### Platform UI

- `platform/web/components/request-console.tsx`
- `platform/web/components/governed-request-list-client.tsx`
- `platform/web/components/policy-profile-client.tsx`
- `platform/web/components/run-detail-client.tsx`

## Change Checklist For Maintainers

When changing request/control behavior, check all of these:

1. Does the request still pass through the intended layers?
2. Did any path bypass HITL or change approval semantics?
3. Did Layer 4 start doing execution work again?
4. Did Layer 5 gain a write path that is not declared?
5. Does dry-run still avoid all real writes?
6. Is failure evidence still preserved?
7. Does audit still capture the outcome?
8. Do tests still cover the changed path?

## Tests To Recheck

Core areas:

- `tests/test_agent_control_stack.py`
- `tests/test_platform_control.py`
- `tests/test_platform_hitl.py`
- `tests/test_platform_lock.py`
- `tests/test_platform_policy_feedback.py`
- `tests/test_platform_rollback.py`

At minimum after meaningful control-path changes, re-run:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

And for the reference web app:

```powershell
cd platform\web
npm run build
```

## Known V1 Limitation

The clearest documented remaining product gap is:

- platform policy edits are versioned and audited, but are not yet automatically written back into connected repo policy artifacts

Do not remove that note from docs until the repo writeback path actually exists.

## How To Use The Issue Tracker

The public issue tracker is intentionally used as the production-readiness backlog.

That means issues may represent:

- missing features
- verification tasks
- documentation hardening
- regression protection

The issue tracker is not only a bug bucket.
It is the system-completeness contract for the open-source reference implementation.
