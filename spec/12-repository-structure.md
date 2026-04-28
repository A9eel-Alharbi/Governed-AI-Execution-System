# Section 12: AOS/CDD v2 Repository Structure

The vault lives inside the repository because out-of-repo governance always drifts. Constraints must sit near the code they govern, not in a wiki.

```text
/aos-cdd-v2/                              # Framework package root when used standalone or vendored into another repository
  README.md                               # Entry point for framework users
  spec/                                   # Canonical human-readable specification
  _templates/                             # Reusable templates for all required artifacts
    constraints/                          # Templates for schema, API, testing, security
    work-packages/                        # WP and CCR templates
    ops/                                  # Session loader, dashboard, command registry templates
  machine/                                # Schemas used by CI validators and automation
  examples/                               # Worked examples
    saas-api/                             # Multi-tenant SaaS API example
      constraints/                        # Example constraint documents
      work-packages/                      # Example WPs
      sessions/                           # Example session loaders and completion reports
      ops/                                # Example dashboard, command registry, and CCR artifacts
```

In a real application repository, the preferred structure is:

```text
/docs/aos/vision/vision.md                # Strategy layer
/services/api/aos/constraints/            # API-local constraints
/services/api/aos/work-packages/          # API work packages
/services/api/aos/sessions/               # API session loaders and reports
/infra/aos/constraints/security.md        # Infra and security constraints
/aos/health/vault-health.yaml             # Repository-wide machine-readable health dashboard
/aos/registry/commands.yaml               # Command registry
/aos/_templates/                          # Local project templates, derived from the framework
```

Colocation rule:

- Schema constraints live next to migrations or schema definitions.
- API contracts live next to the service exposing the API.
- Security and testing strategy can be shared if they are organization-wide.
- The health dashboard may aggregate across services, but source artifacts remain local.
