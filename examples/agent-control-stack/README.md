# Agent Control Stack Example

This example models a product that combines an interpretation-control layer with AOS/CDD-governed execution.

The product goal is to move from raw user request to one explicit outcome:

- clarify
- refuse
- dispatch
- change-control

The example is intentionally small. It defines the initial constraint set, one command registry, one health dashboard, and the first implementation work package.

## Runnable Slice

The repository also includes a small Python package under `agent_control_stack/` that demonstrates the first governed pipeline slice:

- restore
- balance
- classify
- dispatch

Example:

```powershell
python -m agent_control_stack.cli --text "Run WP-001 now" --context examples\agent-control-stack\runtime\run-wp-context.yaml
```

That command should return a `dispatch` decision envelope targeting the governed AOS/CDD session path for `WP-001`.

To execute and persist the full alpha flow:

```powershell
python -m agent_control_stack.cli --text "Run WP-001 now" --context examples\agent-control-stack\runtime\run-wp-context.yaml --execute --persist
```

That command writes the decision and execution outputs to `runs/`.

## HTTP API

Run the alpha service:

```powershell
python -m agent_control_stack.service --port 8000
```

Example request:

```powershell
@'
{
  "text": "Run WP-001 now",
  "context": {
    "repository_root": "/home/dmin/viktor-devin/workspace/governed-ai-quickstart/repo",
    "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
    "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml"
  },
  "execute": true,
  "persist": true
}
'@ | curl.exe -X POST http://127.0.0.1:8000/interpret -H "Content-Type: application/json" --data-binary @-
```

The example policy artifact lives at [ops/policy-profile.yaml](./ops/policy-profile.yaml). It defines staging defaults and higher-risk overrides for validation and protected-resource cases.
