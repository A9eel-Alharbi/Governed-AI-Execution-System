# Agent Control Stack API

This document describes the alpha HTTP API exposed by `agent_control_stack.service`.

The API is intentionally small. It exposes the current governed workflow:

1. interpret a request
2. optionally execute the registered governed procedure
3. optionally persist the run
4. fetch persisted run records

## Start The Service

From the repository root:

```powershell
python -m agent_control_stack.service --port 8000
```

Default base URL:

```text
http://127.0.0.1:8000
```

Deployment guidance for this service is documented in [deployment.md](./deployment.md).

## Endpoints

### `GET /health`

Health check for the service process.

Response:

```json
{
  "status": "ok"
}
```

### `POST /interpret`

Interpret one raw request into a governed decision envelope.

Request body:

```json
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
```

Success response example:

```json
{
  "decision": {
    "raw_input": "Run WP-001 now",
    "restored_input": "Run WP-001 now",
    "normalized_input": "Run WP-001 now",
    "outcome": "dispatch",
    "case_id": "implementation.run_wp",
    "rationale": "The request is clear enough to proceed through a registered governed path.",
    "restoration_trace": [],
    "balancing_trace": [],
    "dispatch_target": {
      "case_id": "implementation.run_wp",
      "procedure": "run_governed_work_package",
      "target": "examples/agent-control-stack/sessions/session-WP-001.yaml",
      "human_review_gate": true
    }
  },
  "execution": {
    "procedure": "run_governed_work_package",
    "target": "examples/agent-control-stack/sessions/session-WP-001.yaml",
    "status": "ready",
    "summary": "Prepared governed execution plan for WP-001.",
    "artifacts": [
      "D:/Projects/mygithub/v2/aos-cdd-v2/examples/agent-control-stack/sessions/session-WP-001.yaml"
    ],
    "payload": {
      "work_package_id": "WP-001",
      "constraints_to_load": [
        "examples/agent-control-stack/constraints/schema.md"
      ],
      "done_criteria_reference": {
        "document": "examples/agent-control-stack/work-packages/WP-001-decision-envelope-and-case-registry.md",
        "section": "6. Done Criteria"
      }
    }
  },
  "persistence": {
    "run_id": "run-20260429T000000000000Z",
    "decision_path": "runs/run-20260429T000000000000Z/decision.json",
    "execution_path": "runs/run-20260429T000000000000Z/execution.json"
  }
}
```

Status codes:

- `200 OK`: request interpreted successfully
- `422 Unprocessable Content`: request maps to `clarify`
- `403 Forbidden`: request maps to `refuse`
- `409 Conflict`: request maps to `escalate` or execution failed
- `400 Bad Request`: malformed request body
- `400 Bad Request` with `invalid_policy`: malformed request-scoped policy object

### `POST /execute`

Execute a previously produced dispatch decision.

Request body:

```json
{
  "decision": {
    "raw_input": "Open a CCR for a constraint conflict",
    "restored_input": "Open a CCR for a constraint conflict",
    "normalized_input": "Open a CCR for a constraint conflict",
    "outcome": "dispatch",
    "case_id": "change.constraint_conflict",
    "rationale": "The request is clear enough to proceed through a registered governed path.",
    "restoration_trace": [],
    "balancing_trace": [],
    "dispatch_target": {
      "case_id": "change.constraint_conflict",
      "procedure": "open_constraint_change_request",
      "target": "_templates/work-packages/constraint-change-request.yaml",
      "human_review_gate": true
    }
  },
  "context": {
    "repository_root": "D:/Projects/mygithub/v2/aos-cdd-v2",
    "output_dir": "D:/Projects/mygithub/v2/aos-cdd-v2/runtime-output/ccr",
    "constraint_document": "examples/agent-control-stack/constraints/schema.md"
  },
  "persist": true
}
```

Status codes:

- `200 OK`: execution completed
- `400 Bad Request`: malformed execute payload or invalid decision shape
- `409 Conflict`: execution could not proceed with supplied context

### `GET /runs`

List persisted run summaries.

Response:

```json
{
  "runs": [
    {
      "run_id": "run-20260429T000000000000Z",
      "persisted_at": "2026-04-29T00:00:00+00:00",
      "outcome": "dispatch",
      "case_id": "implementation.run_wp",
      "has_execution": true
    }
  ]
}
```

### `GET /runs/{id}`

Fetch one persisted run, including decision and optional execution payload.

Status codes:

- `200 OK`: run found
- `404 Not Found`: run id does not exist

## Outcome Semantics

The API returns exactly one top-level decision outcome:

- `clarify`: more information is required before execution
- `refuse`: the request is unsafe, contradictory, or out of scope
- `dispatch`: the request is allowed to proceed through a registered governed path
- `escalate`: the case is known but requires higher-order intervention

## Policy Context

The runtime now supports two policy inputs:

- `context.policy_artifact`: path to a governed repo-native policy profile
- `context.policy`: optional request-scoped override object layered on top of the artifact defaults and case overrides

Resolution order is:

1. artifact defaults
2. artifact case overrides for the classified case
3. request-scoped `context.policy`
4. legacy flat context keys, if present

Current fields:

- `environment`: `dev | staging | prod`
- `approval_state`: `unapproved | approved`
- `target_class`: `general | security | production | infrastructure`
- `destructive_action`: `true | false`
- `path_privilege`: string token for approved protected-resource access

Example:

```json
{
  "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
  "policy": {
    "path_privilege": "security-approved"
  }
}
```

## Current Alpha Limits

- classification is still heuristic, not learned
- restoration and balancing are still narrow compared with the larger product vision
- governed execution currently prepares or drafts artifacts; it does not yet run a full autonomous coding lifecycle

Compatibility expectations for this API are documented in [compatibility.md](./compatibility.md).
