# Compatibility Policy

This document defines the compatibility expectations for the combined `AOS/CDD` framework and `agent_control_stack` runtime.

## Scope

There are three compatibility surfaces in this repository:

1. `machine-readable AOS/CDD artifacts`
2. `agent_control_stack` HTTP and CLI contracts
3. `generated operational reports`

These surfaces evolve at different speeds and should not be treated as equally stable.

## Stability Levels

### 1. AOS/CDD Artifact Schemas

Examples:

- session loaders
- vault health dashboards
- command registries
- CCR artifacts
- policy profiles

Policy:

- `patch` releases may clarify docs or tooling behavior without changing required schema fields
- `minor` releases may add optional fields
- fields that become newly required must wait for a `minor` release and include migration guidance
- removing a field or changing its meaning is a breaking change

### 2. Agent Control Stack API and CLI

Examples:

- `POST /interpret`
- `POST /execute`
- `GET /runs`
- CLI JSON payload shapes

Policy:

- top-level decision outcomes remain: `clarify`, `refuse`, `dispatch`, `escalate`
- existing response fields should not be removed in patch releases
- new optional response fields may be added in minor releases
- changing status-code meaning, removing fields, or renaming fields is a breaking change

### 3. Operational Reports

Examples:

- eval summary JSON
- policy gate JSON
- run report JSON
- vault health report JSON

Policy:

- reports may add optional fields in patch or minor releases
- core summary keys used by CI gates should not change without migration guidance
- downstream automation should ignore unknown fields

## Versioning Rules

This repo currently uses:

- framework version: `2.0.0`
- package version: see [pyproject.toml](../pyproject.toml)

Recommended interpretation:

- `major`: breaking compatibility across machine-readable artifacts or public runtime contracts
- `minor`: backward-compatible additions, new optional fields, new procedures, new reports
- `patch`: fixes, doc clarifications, validation improvements, non-breaking hardening

## Breaking Change Discipline

Any breaking change should include:

- changelog entry
- migration notes
- updated examples
- validator updates if machine-readable artifacts change
- test updates proving the new contract

## Consumer Guidance

If you integrate with this repo:

- validate machine-readable artifacts rather than assuming shape
- ignore unknown JSON fields where possible
- pin versions for production use
- review the changelog before upgrading

## Current Reality

This repository is approaching production maturity, but some runtime surfaces are still better treated as `beta-stable` than permanently frozen.

In practice:

- AOS/CDD artifact compatibility is the strongest contract
- decision outcome vocabulary is stable
- reporting and operational fields may still expand
