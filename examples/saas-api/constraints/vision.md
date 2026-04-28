# Multi-Tenant SaaS API Vision

## Document Control

- Document ID: `vision-saas-core`
- Owner: `Product Lead`
- Last validated: `2026-04-28`
- Adoption tier: `Tier 2`

## Product Purpose

This product provides a multi-tenant API for SaaS companies to manage tenant subscriptions, resource usage, and access control from one service instead of stitching billing, entitlement, and reporting data across multiple systems.

## Target Users

- `Primary: platform engineering teams at B2B SaaS companies with 10 to 100 engineers`
- `Primary: revenue operations teams that need consistent usage reporting for billing`
- `Secondary: customer success tooling teams exposing subscription state to internal portals`

## In Scope

- `Tenant-aware authentication and authorization`
- `Subscription CRUD and status lifecycle`
- `Usage event aggregation and daily reporting`
- `Background sync with billing provider`

## Out of Scope

- `Customer-facing dashboard UI`
- `Real-time streaming analytics`
- `Multi-region active-active deployment in phase one`

## Architecture Direction Decisions

| Decision | Status | Rationale |
|---|---|---|
| `PostgreSQL primary database` | `approved` | `Relational integrity, tenancy boundaries, and transactional writes are required` |
| `REST API with OpenAPI 3.1 source contract` | `approved` | `Strong machine-readable contracts are required for AI execution` |
| `JWT access tokens plus refresh tokens` | `approved` | `Supports service-to-service and admin-driven access patterns` |

## Non-Functional Requirements

- `P95 latency under 250 ms for standard CRUD endpoints at 150 RPS`
- `99.9% monthly API availability`
- `Support 2,500 tenants and 20 million daily usage events`

## Questions Not Yet Answered

- `Will entitlements be modeled as plan snapshots or dynamic feature evaluations?`
- `Should billing provider sync be pull-based, webhook-based, or hybrid?`

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-28` | `OpenAI Codex` | `Initial example` |
