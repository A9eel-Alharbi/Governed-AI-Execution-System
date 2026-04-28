# Start Here

This repository solves one problem: AI coding sessions are fast but unreliable unless their scope, constraints, and completion contract are explicit.

If you are new to AOS/CDD v2, do not start by reading every file.

## Choose Your Entry Path

### I want the minimum viable path

Start in [quickstart](../quickstart/README.md).

Use this if:

- you are a solo builder
- you are testing the idea
- you want Tier 1 only

### I want to understand the framework

Read in this order:

1. [README.md](../README.md)
2. [spec/01-architecture.md](../spec/01-architecture.md)
3. [spec/03-tiered-adoption.md](../spec/03-tiered-adoption.md)
4. [spec/13-agent-onboarding-prompt.md](../spec/13-agent-onboarding-prompt.md)
5. [spec/14-worked-example.md](../spec/14-worked-example.md)

### I want to copy this into a real repo

Start with:

1. `quickstart/` if you are doing Tier 1
2. `_templates/` if you are doing Tier 2 or Tier 3

Then validate with:

```powershell
python tools\aos_validate.py validate
python tools\aos_validate.py health-report
```

## What This Repo Contains

- `spec/`: the framework definition
- `_templates/`: reusable project artifacts
- `machine/`: schemas for validator-enforced files
- `tools/`: reference validator
- `examples/`: worked example
- `quickstart/`: lowest-friction entry path

## What This Repo Does Not Do

It does not replace product management, team process, or architecture judgment. Read [spec/15-boundaries.md](../spec/15-boundaries.md) before adopting it broadly.
