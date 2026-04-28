# Tier 1 Quickstart

This directory is the minimum viable entry path for AOS/CDD v2.

Use this when you want the consistency benefits of the framework without adopting the full repository structure on day one.

## Goal

Get to a usable Tier 1 setup in one sitting:

1. Fill out a one-page vision.
2. Declare your schema source of truth.
3. Declare your API contract source of truth.
4. Declare your auth/secrets rules.
5. Track health manually in one YAML file.

## Files

- `vision.md`: smallest acceptable strategy layer
- `schema.md`: smallest acceptable schema constraint
- `api-contract.md`: smallest acceptable API companion
- `security-rules.md`: smallest acceptable security rules
- `vault-health.yaml`: smallest acceptable health tracker

## What To Skip At Tier 1

- full work package library
- CCR workflow unless constraints are changing often
- command registry
- impact assessments
- failure-path artifact library

## Honest Setup Time

- New project with clear architecture: 1 to 2 hours
- Existing project with drift: 2 to 4 hours

This is the realistic "first useful use" path. The fuller templates remain in `_templates/`.
