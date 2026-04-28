# Section 2: Redesigned Document Templates

The framework treats templates as operational artifacts. They live in `_templates/` because teams must copy, validate, and review them in-source. This section defines which template is canonical for each artifact type and why each format was chosen.

## Template Inventory

| Requirement | Canonical Template | Format Choice | Reason |
|---|---|---|---|
| Vision document | `_templates/constraints/vision.md` | `Markdown` | Human-authored strategic content needs readability and reviewability more than rigid machine validation. |
| Database schema constraint | `_templates/constraints/schema.md` | `Markdown with embedded DDL reference` | Schema governance needs narrative rules plus canonical migration linkage. |
| API contracts | `_templates/constraints/api-contract.openapitmpl.yaml` plus `_templates/constraints/api-contract.md` | `OpenAPI YAML plus Markdown companion` | OpenAPI is the machine-readable source of truth; Markdown captures operational rules not modeled cleanly in OpenAPI. |
| Testing strategy | `_templates/constraints/testing-strategy.md` | `Markdown` | Policy-heavy artifact with checklist semantics. |
| Security rules | `_templates/constraints/security-rules.md` | `Markdown` | Governance artifact with manual validation and sign-off. |
| Work package | `_templates/work-packages/work-package.md` | `Markdown` | Review-focused, high-context artifact. |
| Session loader | `_templates/ops/session-loader.yaml` | `YAML` | Human-editable machine-readable format used frequently at runtime. |
| Command registry | `_templates/ops/command-registry.yaml` | `YAML` | Small registry file that benefits from readability and structured validation. |
| Constraint change request | `_templates/work-packages/constraint-change-request.yaml` | `YAML` | Structured approval workflow with automation hooks. |
| Vault health dashboard | `_templates/ops/vault-health.yaml` | `YAML` | CI-generated structured status document intended for both humans and tooling. |

## Format Rules

YAML is preferred for machine-readable operational files because teams inspect and edit them directly during normal development. JSON is still used for schemas in the `machine/` directory because validator tooling expects it widely and because JSON Schema is the practical interoperability standard.

OpenAPI YAML is mandatory for API contracts. Prose-only API descriptions are forbidden in v2 because they cannot be diffed or validated reliably.

The OpenAPI template supports an `x-aos` extension for governance metadata at the endpoint level. The extension is intentionally separate from the business schema because ownership, stability class, and change classification are delivery controls, not public API semantics. Its shape is defined in `machine/x-aos.schema.json`.

Markdown remains the preferred format for governance documents when the artifact contains rationale, policy, exclusions, or decisions that are reviewed by humans first and machines second.

## Validation Pairing

Each machine-readable template should have a validator schema where practical:

- `machine/context-loader.schema.json`
- `machine/vault-health.schema.json`
- `machine/command-registry.schema.json`
- `machine/ccr.schema.json`
- `machine/completion-report.schema.json`
- `machine/x-aos.schema.json`

This pairing closes a v1 gap. A structured-looking file that is never validated is still ceremonial documentation.

## Source-of-Truth Rule for Work Packages and Session Loaders

The work package is the authoritative definition of which constraints must be loaded and what permission level applies to each one. The session loader is a runtime artifact derived from the work package plus session-specific state such as prior blockers and health status.

That means:

- the WP constraint table is normative
- the session loader must include every WP-declared constraint
- the session loader may include additional runtime metadata, but it may not silently drop or weaken a WP-declared permission

If the two disagree, validation must fail and the session loader must be regenerated or corrected before execution.
