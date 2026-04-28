# Contributing

## Scope

This repository is a framework project, not an application project. Contributions should improve one or more of these layers:

- framework specification
- reusable templates
- validator and automation tooling
- worked examples
- onboarding and adoption materials

## Contribution Rules

1. Keep the framework repository-native. Do not move core guidance into external documents.
2. Prefer concrete enforcement over aspirational prose.
3. If you add a machine-readable artifact, add or update its schema in `machine/`.
4. If you change a workflow expectation, update both the spec and the worked example.
5. If you introduce new required fields, document the compatibility impact clearly.

## Development Workflow

1. Make your changes.
2. Run:

```powershell
python tools\aos_validate.py validate
python tools\aos_validate.py health-report
```

3. Confirm the example artifacts still validate.
4. Update relevant docs in `spec/`, `_templates/`, `quickstart/`, or `examples/`.

## Pull Requests

Every pull request should state:

- what problem it fixes
- what files or artifact types it affects
- whether it changes the machine-readable contract
- whether it changes onboarding or adoption expectations

## High-Value Contribution Areas

- stronger cross-document validation
- better quickstart/bootstrap tooling
- richer example projects
- better CI integrations
- migration guidance between framework versions
