# Alpha Release Checklist

Use this checklist before publishing the first public alpha of the combined system.

## Product Framing

- [ ] The README clearly explains the split between `AOS/CDD` and `agent_control_stack`.
- [ ] The project is described as an `alpha`, not as a finished standard.
- [ ] The current limitations are stated plainly.

## Repository Hygiene

- [ ] `.gitignore` excludes generated runtime and test output.
- [ ] Generated directories are removed from the release commit where possible.
- [ ] Packaging metadata is present in `pyproject.toml`.
- [ ] Required runtime files are included through `MANIFEST.in` and package-data rules.

## Docs

- [ ] `README.md` explains what the repository is.
- [ ] `QUICKSTART.md` gives a 5-10 minute first run path.
- [ ] `docs/api.md` documents the HTTP API.
- [ ] `docs/architecture.md` explains how the two systems fit together.
- [ ] `docs/compatibility.md` explains upgrade and compatibility expectations.
- [ ] `docs/deployment.md` explains the current production-like deployment posture.
- [ ] `examples/agent-control-stack/README.md` explains the governed example.

## Functionality

- [ ] CLI flow works.
- [ ] HTTP service works.
- [ ] Persistence works.
- [ ] Template-driven AOS/CDD artifact generation works.
- [ ] The current governed case families work:
  - [ ] `new_project.initial_definition`
  - [ ] `implementation.create_first_wp`
  - [ ] `implementation.run_wp`
  - [ ] `implementation.review_wp`
  - [ ] `implementation.create_followup_wp`
  - [ ] `change.constraint_conflict`
  - [ ] `docs.update_constraints`
  - [ ] `ops.run_validation`
  - [ ] `security.protected_resource_change`

## Verification

- [ ] Unit tests pass.
- [ ] HTTP service tests pass.
- [ ] Scenario tests pass.
- [ ] `python tools\aos_validate.py validate` passes.
- [ ] `python -m agent_control_stack.eval` passes.
- [ ] `python -m agent_control_stack.policy_gate --eval-report reports/agent-control-eval.json` passes.
- [ ] `python -m agent_control_stack.ops_report --store-dir runs` produces a valid report.
- [ ] `python -m agent_control_stack.run_maintenance --store-dir runs` reports retention state without error.

## Release Positioning

- [ ] Version is set intentionally.
- [ ] Changelog entry or release notes are prepared.
- [ ] The release note includes both claims and non-claims.
- [ ] The release note explains that Tier 3 is roadmap work, not current alpha scope.

## Recommended First Release Message

The first public release should be framed roughly like this:

`This alpha introduces a governed interpretation and dispatch layer for agentic software-development requests, integrated with AOS/CDD execution artifacts and workflows. It is intended for evaluation, experimentation, and extension rather than production-wide standardization.`
