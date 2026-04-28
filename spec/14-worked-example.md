# Section 14: Worked Example

The worked example demonstrates AOS/CDD v2 on a realistic multi-tenant SaaS API. The purpose is not to show every possible artifact. The purpose is to prove that the framework can be used as an execution system with real constraints, real work packages, and a real change event.

## Example Artifact Map

Core example files:

- Vision: [examples/saas-api/constraints/vision.md](../examples/saas-api/constraints/vision.md)
- Schema: [examples/saas-api/constraints/schema.md](../examples/saas-api/constraints/schema.md)
- API contract: [examples/saas-api/constraints/openapi.yaml](../examples/saas-api/constraints/openapi.yaml)
- Health dashboard: [examples/saas-api/ops/vault-health.yaml](../examples/saas-api/ops/vault-health.yaml)
- Command registry: [examples/saas-api/ops/command-registry.yaml](../examples/saas-api/ops/command-registry.yaml)
- Session loader: [examples/saas-api/sessions/session-WP-002.yaml](../examples/saas-api/sessions/session-WP-002.yaml)
- Completion report: [examples/saas-api/sessions/completion-report-WP-002.yaml](../examples/saas-api/sessions/completion-report-WP-002.yaml)
- Blocker report: [examples/saas-api/sessions/blocker-report-WP-002-plan-key.yaml](../examples/saas-api/sessions/blocker-report-WP-002-plan-key.yaml)
- Conflict report: [examples/saas-api/sessions/conflict-report-WP-002-plan-key.yaml](../examples/saas-api/sessions/conflict-report-WP-002-plan-key.yaml)
- Blocked completion report: [examples/saas-api/sessions/completion-report-WP-002-blocked.yaml](../examples/saas-api/sessions/completion-report-WP-002-blocked.yaml)
- Re-issued session loader: [examples/saas-api/sessions/session-WP-002-post-CCR.yaml](../examples/saas-api/sessions/session-WP-002-post-CCR.yaml)
- CCR: [examples/saas-api/ops/CCR-001-plan-code-rename.yaml](../examples/saas-api/ops/CCR-001-plan-code-rename.yaml)
- Impact assessment: [examples/saas-api/ops/impact-assessment-CCR-001.yaml](../examples/saas-api/ops/impact-assessment-CCR-001.yaml)
- Red health snapshot: [examples/saas-api/ops/vault-health-after-CCR.yaml](../examples/saas-api/ops/vault-health-after-CCR.yaml)

Work packages:

- [WP-001-add-subscriptions-schema.md](../examples/saas-api/work-packages/WP-001-add-subscriptions-schema.md)
- [WP-002-create-subscription-endpoint.md](../examples/saas-api/work-packages/WP-002-create-subscription-endpoint.md)
- [WP-003-auth-login.md](../examples/saas-api/work-packages/WP-003-auth-login.md)
- [WP-004-daily-usage-job.md](../examples/saas-api/work-packages/WP-004-daily-usage-job.md)
- [WP-005-billing-provider-sync.md](../examples/saas-api/work-packages/WP-005-billing-provider-sync.md)

## Scenario Summary

The product exposes tenant authentication, subscription CRUD, usage ingestion, and daily usage reporting. The example starts from a healthy vault state, executes a subscription endpoint work package, and then introduces a breaking schema rename through a CCR to demonstrate propagation and restart behavior.

## Sample Agent Onboarding Session

Human command:

```text
/wp WP-002
```

Agent preflight summary:

```text
Session loaded: session-WP-002-01
WP loaded: WP-002
Dependencies checked: WP-001 done
Health checked: all referenced constraints green
Permissions checked:
- schema.md READ-ONLY
- openapi.yaml READ-ONLY
- vision.md ADVISORY
Proceeding with implementation.
```

Agent completion output is represented by [completion-report-WP-002.yaml](../examples/saas-api/sessions/completion-report-WP-002.yaml).

## Example Change Propagation Event

After WP-002 begins, the team decides `subscriptions.plan_code` is the wrong canonical field name. That is a Class 3 breaking change because:

- it changes the schema
- it changes the API contract field mapping
- it affects in-flight endpoint work
- it affects the planned billing provider sync

The change is recorded in [CCR-001-plan-code-rename.yaml](../examples/saas-api/ops/CCR-001-plan-code-rename.yaml).

The impact assessment in [impact-assessment-CCR-001.yaml](../examples/saas-api/ops/impact-assessment-CCR-001.yaml) shows:

- `WP-002` must stop and be replaced or re-scoped
- `WP-005` must be updated before execution

The failure-path artifacts show what that looks like operationally:

- the agent emits [blocker-report-WP-002-plan-key.yaml](../examples/saas-api/sessions/blocker-report-WP-002-plan-key.yaml)
- the conflicting assumptions are captured in [conflict-report-WP-002-plan-key.yaml](../examples/saas-api/sessions/conflict-report-WP-002-plan-key.yaml)
- the interrupted execution is captured in [completion-report-WP-002-blocked.yaml](../examples/saas-api/sessions/completion-report-WP-002-blocked.yaml)
- the health state turns red in [vault-health-after-CCR.yaml](../examples/saas-api/ops/vault-health-after-CCR.yaml)
- execution can only resume from the re-issued loader [session-WP-002-post-CCR.yaml](../examples/saas-api/sessions/session-WP-002-post-CCR.yaml)

That is the point of the v2 change protocol: the framework knows which WPs referenced the changed constraint and turns the change into an explicit execution event instead of leaving drift for the next agent to discover accidentally.

## Why This Example Matters

This example proves five things:

1. The framework can represent a realistic SaaS domain with multiple bounded constraints.
2. Work packages can be written tightly enough for agent execution.
3. Session loading can be machine-readable and scoped.
4. Completion evidence can be structured and auditable.
5. Breaking changes propagate through the vault instead of silently corrupting work in progress.
