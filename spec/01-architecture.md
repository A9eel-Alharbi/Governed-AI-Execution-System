# Section 1: Redesigned Architecture Overview

## Architecture Summary

AOS/CDD v2 keeps the layered vault model but separates execution state from session loading and separates governance from health. v1 blurred execution planning, runtime context, and done criteria into a single gray area. v2 splits them into distinct layers with explicit ownership and validation.

The architecture uses six layers and one cross-cutting subsystem:

1. Strategy Layer
2. Constraint Layer
3. Execution Layer
4. Session Layer
5. Command Layer
6. Health Layer
7. Change Protocol Subsystem

The Health Layer is explicit rather than embedded. That choice increases surface area slightly, but it eliminates a common failure mode: teams assuming constraints are valid because they exist. Constraint validity is now a first-class operational concern.

The Change Protocol is modeled as a subsystem rather than a layer because it acts across Constraint, Execution, Session, and Health artifacts.

## Textual Diagram

`Strategy -> Constraints -> Execution -> Session -> Command -> Agent Execution`

Cross-cutting controls:

- `Health` validates `Strategy`, `Constraints`, and `Execution references`.
- `Change Protocol` propagates updates from `Constraints` into `Execution`, `Session`, and `Health`.

## Structured Layer Outline

| Layer | Purpose | Owner | Update Frequency | Staleness Risk | Machine-Readable Target |
|---|---|---|---|---|---|
| Strategy Layer | Defines product intent, boundaries, and unresolved decisions before detailed constraints are authored. | Product lead or staff engineer | Monthly or per major initiative | Medium | Partial |
| Constraint Layer | Defines the implementation boundaries the agent is allowed to rely on. | Technical owner per domain | Weekly or per relevant change | High | Yes |
| Execution Layer | Breaks work into atomic, reviewable units with explicit scope and dependency declarations. | Engineering lead or delivery owner | Daily to weekly | High | Partial |
| Session Layer | Loads the exact runtime context for one agent session in machine-readable form. | Agent operator or automation | Per session | High | Yes |
| Command Layer | Maps human commands to work packages or operational actions. | Team lead or tooling owner | Infrequent once stable | Low | Partial |
| Health Layer | Tracks whether vault artifacts are current, validated, contradictory, or unsafe to trust. | Tooling owner with domain sign-off | Automated after each merge; manual weekly | High | Yes |

## High-Stability vs Low-Stability Constraints

High-stability constraints change rarely and must be governed tightly. They include database schema core entities, authentication method, authorization policy, audit columns, tenancy model, and security requirements. These documents default to `READ-ONLY` or `PROPOSE` for agents.

Low-stability constraints change often and need lighter governance. They include API payload fields before public release, feature flags, UI contracts in active design, and internal workflow rules. These can use `ADVISORY` or `IMPLEMENT WITH REVIEW` when the work package explicitly allows it.

## Adoption Tier Compatibility

The architecture is shared across all tiers. Tier 1 uses only a subset of the artifacts. Tier 2 activates the full execution discipline. Tier 3 adds automation, health gates, tracker sync, and CI integration. The model does not fork by tier.
