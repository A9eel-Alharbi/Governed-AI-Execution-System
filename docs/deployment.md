# Deployment Guide

This document describes the intended deployment posture for the current `agent_control_stack` service.

## Current Deployment Model

The runtime is intentionally simple:

- Python process
- local filesystem run store
- JSON HTTP API
- validator and report commands run beside it

This is suitable for:

- internal tools
- controlled pilots
- small-team environments
- staging-like governed workflows

It is not yet a full multi-tenant hosted platform.

## Recommended Runtime Topology

For a production-like deployment, use:

1. one service instance behind a reverse proxy
2. TLS terminated at the proxy
3. dedicated writable directory for run storage
4. scheduled ops jobs for:
   - eval generation
   - policy gate checks
   - run reports
   - expired-run maintenance

## Required Environment Assumptions

- Python `3.11+`
- writable run store directory
- repo checkout available to the service if governed execution is enabled
- secret material provided outside the repo

## Recommended Operational Defaults

- bind the service to loopback or an internal network only
- put authn/authz in front of the current HTTP service
- treat `runs/` as operational data, not source control
- review protected-resource scenarios before enabling broader automation
- keep `repository_root` constrained to approved repos only

## Storage Guidance

The default run store is filesystem-based.

Recommended practice:

- use a dedicated directory outside the source tree in real deployment
- back up or export reports separately from raw runs
- configure retention explicitly using `retention_days`
- run maintenance regularly:

```powershell
python -m agent_control_stack.run_maintenance --store-dir runs
python -m agent_control_stack.run_maintenance --store-dir runs --delete
```

## Operational Commands

Examples:

```powershell
python -m agent_control_stack.service --host 127.0.0.1 --port 8000
python -m agent_control_stack.eval > reports\agent-control-eval.json
python -m agent_control_stack.policy_gate --eval-report reports\agent-control-eval.json
python -m agent_control_stack.ops_report --store-dir runs
python -m agent_control_stack.run_maintenance --store-dir runs
```

## Security Notes

- do not expose the raw service publicly without a fronting auth layer
- do not share a writable run store between unrelated deployments unless you control ownership and cleanup
- keep policy artifacts and threat-model artifacts under review
- use the validator in CI before shipping artifact changes

## Upgrade Guidance

Before upgrading:

1. read [CHANGELOG.md](../CHANGELOG.md)
2. read [docs/compatibility.md](./compatibility.md)
3. run:
   - validator
   - tests
   - eval
   - policy gate

## Platform API Extension

The hosted `platform/api` layer now supports:

- PostgreSQL-backed persistence through `AOS_CDD_PLATFORM_DATABASE_URL`
- external trusted-header auth mode through:
  - `AOS_CDD_PLATFORM_AUTH_MODE=external`
  - `AOS_CDD_PLATFORM_AUTH_PROVIDER`
  - `AOS_CDD_PLATFORM_AUTH_LOGIN_PATH`
  - `AOS_CDD_PLATFORM_AUTH_USER_*_HEADER`

Recommended deployment pattern:

1. put the platform API behind a reverse proxy or gateway
2. terminate TLS there
3. let the gateway inject trusted user headers
4. run the API against PostgreSQL for durable state
5. run the Next.js frontend against that API with matching auth mode

## Current Limits

- external auth assumes a trusted fronting gateway; it is not a full identity provider by itself
- no distributed locking model
- no formal HA story

Those are known limitations, not hidden ones.
