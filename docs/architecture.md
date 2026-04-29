# Architecture

This repository now contains two connected systems.

## 1. AOS/CDD

AOS/CDD is the original framework in this repository.

Its purpose is to govern AI-assisted software delivery inside a codebase through:

- project constraints
- work packages
- session loaders
- health dashboards
- completion and change-control artifacts

It answers questions like:

- What is the project?
- What is the exact bounded task?
- Which constraints may the agent rely on?
- What evidence proves the work is done?
- What happens when constraints change?

### AOS/CDD Tiers

- `Tier 1`: lightweight constraint-first onboarding
- `Tier 2`: full work-package and session-based execution discipline
- `Tier 3`: integrated operations, validation, and automation

## 2. Agent Control Stack

The `agent_control_stack` package is the complementary system added on top of the original framework.

Its purpose is to govern how a raw user request becomes an allowed action.

It answers questions like:

- What does the user mean?
- Is the request ambiguous?
- Is it contradictory?
- Is it out of scope?
- Which governed procedure is allowed to run?

Its core pipeline is:

- `Restore`
- `Balance`
- `Classify`
- `Dispatch`

And it returns exactly one top-level outcome:

- `clarify`
- `refuse`
- `dispatch`
- `escalate`

## How The Systems Fit Together

The systems are not alternatives.

They operate at different layers:

1. `Agent Control Stack`
   Interprets the request and decides whether execution is allowed.

2. `AOS/CDD`
   Governs the execution path once the request is approved.

So the combined flow is:

```text
Raw Request
  -> Restore
  -> Balance
  -> Classify
  -> Policy Decision
  -> Clarify / Refuse / Dispatch / Escalate
  -> If Dispatch:
     -> AOS/CDD Tier 1 or Tier 2 Path
     -> Constraints
     -> Work Package
     -> Session Loader
     -> Session-declared Policy Profile
     -> Governed Execution
     -> Completion / Change-Control Artifacts
```

## Current Alpha Case Families

The current alpha supports these registered case families:

- `new_project.initial_definition`
- `implementation.create_first_wp`
- `implementation.run_wp`
- `implementation.review_wp`
- `implementation.create_followup_wp`
- `change.constraint_conflict`
- `docs.update_constraints`
- `ops.run_validation`
- `security.protected_resource_change`

## Repository Map

Original AOS/CDD areas:

- `spec/`
- `_templates/`
- `machine/`
- `tools/`
- `quickstart/`
- `examples/saas-api/`

New complementary system:

- `agent_control_stack/`
- `examples/agent-control-stack/`
- `docs/api.md`
- `tests/`

## What “V1 Complete” Means Here

For this repository, `V1 complete` does not mean universal autonomy.

It means:

- requests can be interpreted into stable governed outcomes
- approved cases can hand off into AOS/CDD paths
- runs can be executed through CLI and HTTP
- traces and results can be persisted
- behavior is covered by unit, service, and scenario tests

Tier 3 remains important, but it is best treated as later operational maturity rather than a blocker for the first open-source alpha.
