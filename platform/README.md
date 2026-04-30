# Platform Workspace

This folder is the starting point for the hosted product built on top of the repository-native framework.

The rest of the repository contains the governance engine:

- `agent_control_stack/`: interpretation, policy, approval, dispatch, reporting
- `spec/`, `_templates/`, `machine/`, `tools/`: the AOS/CDD framework
- `examples/`: governed example projects

This `platform/` folder is where the user-facing product can be built.

## Product Idea

The product form is:

1. a website where users create a project
2. a backend that stores project/account state
3. a control API that runs `agent_control_stack`
4. repo integration that writes and reads AOS/CDD artifacts
5. an execution layer that lets an LLM or tool act only after governance checks pass

In short:

`Website -> Platform Backend -> agent_control_stack -> AOS/CDD -> LLM/tool runner -> Repo -> Reports back to UI`

## Recommended Internal Split

- `web/`
  Frontend application for project creation, dashboards, approvals, work packages, reports, and run history.
- `api/`
  Product backend for auth, project state, repo connections, and orchestration around `agent_control_stack`.
- `shared/`
  Shared contracts between the web app and backend, such as request payloads and response shapes.
- `docs/`
  Product-specific notes, flows, and UI architecture.

## What The Website Should Show

The website should be the control room for humans.

Good first surfaces:

- project list
- project creation flow
- connected repo status
- vision / schema / API / security views
- policy profile view
- approval records view
- work package dashboard
- change-control dashboard
- run history
- decision report view
- validation and ops reports

## First Practical Scope

Build the website around the existing runtime, not around a new model runtime.

The safest first phase is:

1. frontend that submits requests
2. backend that calls the existing `agent_control_stack` service
3. backend that stores product-level metadata
4. repo-backed workflows using the existing artifact model

That keeps the product aligned with the repo's actual engine instead of inventing a second system.
