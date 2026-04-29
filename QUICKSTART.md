# Quickstart

This quickstart is for the current `agent_control_stack` alpha that now lives alongside the original AOS/CDD framework in this repository.

## What You Are Running

This repository now contains two connected systems:

- `AOS/CDD`: the governed execution framework
- `agent_control_stack`: the interpretation and dispatch control layer

The alpha flow is:

1. take a raw request
2. interpret it into `clarify`, `refuse`, `dispatch`, or `escalate`
3. optionally execute the registered governed procedure
4. optionally persist the run

## Requirements

- Python `3.11+`
- `PyYAML`

## Install

From the repository root:

```powershell
python -m pip install -e .
```

## Run The CLI

Dispatch a governed work-package execution:

```powershell
python -m agent_control_stack.cli --text "Run WP-001 now" --context examples\agent-control-stack\runtime\run-wp-context.yaml --execute --persist
```

What you should see:

- a `decision` payload with outcome `dispatch`
- an `execution` payload with status `ready`
- a `persistence` record written under `runs/`

## Run The HTTP API

Start the service:

```powershell
python -m agent_control_stack.service --port 8000
```

Then send a request:

```powershell
@'
{
  "text": "Run WP-001 now",
  "context": {
    "repository_root": "D:/Projects/mygithub/v2/aos-cdd-v2",
    "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
    "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
    "policy": {
      "path_privilege": "repo-approved"
    }
  },
  "execute": true,
  "persist": true
}
'@ | curl.exe -X POST http://127.0.0.1:8000/interpret -H "Content-Type: application/json" --data-binary @-
```

## Try The Four Current Cases

### 1. New project onboarding

```powershell
python -m agent_control_stack.cli --text "Start a new project in this repo" --execute
```

### 2. Create the first work package

```powershell
python -m agent_control_stack.cli --text "Create work package for the first implementation task" --context examples\agent-control-stack\runtime\run-wp-context.yaml --execute
```

### 3. Run a governed work package

```powershell
python -m agent_control_stack.cli --text "Run WP-001 now" --context examples\agent-control-stack\runtime\run-wp-context.yaml --execute
```

### 4. Open a constraint change request

```powershell
python -m agent_control_stack.cli --text "Open a CCR for a constraint conflict" --context examples\agent-control-stack\runtime\run-wp-context.yaml --execute
```

## Validate The AOS/CDD Artifacts

```powershell
python tools\aos_validate.py validate
```

## Run The Tests

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

This now includes scenario-level tests from `tests/scenarios/` in addition to unit and service coverage.

## Run The Eval Summary

```powershell
python -m agent_control_stack.eval
```

That command prints a summary including:

- total scenarios
- passed / failed count
- safe-outcome accuracy
- outcome distribution
- execution-status distribution

## Run The Policy Gate

```powershell
python -m agent_control_stack.eval > reports\agent-control-eval.json
python -m agent_control_stack.policy_gate --eval-report reports\agent-control-eval.json
```

That gate enforces:

- minimum safe-outcome accuracy
- zero failed policy-critical scenarios
- no failures in high-risk categories like `security`, `validation`, and `change-control`

## Inspect Run Retention

```powershell
python -m agent_control_stack.ops_report --store-dir runs
python -m agent_control_stack.run_maintenance --store-dir runs
```

To delete expired runs explicitly:

```powershell
python -m agent_control_stack.run_maintenance --store-dir runs --delete
```

## Policy Artifacts

The preferred path is now a repo-native governed policy artifact:

- [examples/agent-control-stack/ops/policy-profile.yaml](./examples/agent-control-stack/ops/policy-profile.yaml)
- [examples/agent-control-stack/ops/security-threat-model.md](./examples/agent-control-stack/ops/security-threat-model.md)
- [examples/agent-control-stack/ops/APR-001-security-validation.yaml](./examples/agent-control-stack/ops/APR-001-security-validation.yaml)

You can still supply request-scoped policy fields when needed. An example context overlay is available at:

- [examples/agent-control-stack/runtime/security-policy.yaml](./examples/agent-control-stack/runtime/security-policy.yaml)

## Where To Look Next

- High-level framework context: [README.md](./README.md)
- HTTP API details: [docs/api.md](./docs/api.md)
- New system example: [examples/agent-control-stack/README.md](./examples/agent-control-stack/README.md)
- AOS/CDD onboarding docs: [docs/START-HERE.md](./docs/START-HERE.md)
