# Vision Document Template

> Required fields are marked `[required]`. Optional fields are marked `[optional]`.
> Replace all bracketed guidance before using this document.

## Document Control

- Document ID `[required]`: `vision-core`
- Owner `[required]`: `[role and name]`
- Last validated `[required]`: `YYYY-MM-DD`
- Adoption tier `[required]`: `Tier 1 | Tier 2 | Tier 3`

## 1. Product Purpose `[required]`

<!-- State the business problem in one paragraph. Name the buyer or operating stakeholder. -->
Example:
`The product gives finance teams at B2B SaaS companies a tenant-safe API for usage metering and subscription state so they can reconcile billing without custom data pipelines.`

## 2. Target Users `[required]`

<!-- Be specific. Name roles, company type, scale, and pain. Do not write "users". -->
Example:
- `Primary: RevOps managers at SaaS companies with 50 to 500 employees`
- `Secondary: Internal developer platform teams exposing tenant usage data`

## 3. In Scope `[required]`

Example:
- `Tenant-scoped API authentication`
- `Subscription CRUD`
- `Usage aggregation background jobs`

## 4. Out of Scope `[required]`

<!-- Explicit exclusions prevent silent scope creep. -->
Example:
- `Marketplace billing adapters in v1`
- `End-user analytics UI`
- `Per-event real-time billing`

## 5. Architecture Direction Decisions `[required]`

| Decision | Status | Rationale |
|---|---|---|
| `PostgreSQL as system of record` | `approved` | `Need transactional tenancy and relational integrity` |
| `JWT access tokens with refresh tokens` | `approved` | `Supports API clients and revocation flow` |

## 6. Non-Functional Requirements `[required]`

<!-- Include measurable targets. -->
Example:
- `P95 API latency for CRUD endpoints under 300 ms at 200 RPS`
- `99.9% monthly availability for public API`
- `Support 5,000 tenants and 50 million usage events per day`

## 7. Questions Not Yet Answered `[required before Layer 2 is finalized]`

Example:
- `Will subscription changes be event-sourced or state-based?`
- `Will tenant admins support SSO in the first release?`

## 8. Dependencies and Assumptions `[optional]`

Example:
- `Stripe remains the subscription source of truth for the first 12 months`

## Change Log

| Date | Author | Change |
|---|---|---|
| `YYYY-MM-DD` | `[name]` | `Initial draft` |
