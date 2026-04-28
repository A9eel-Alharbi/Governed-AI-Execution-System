# SaaS API Schema Constraint

## Document Control

- Document ID: `schema-saas-core`
- Owner: `Backend Lead`
- Last validated: `2026-04-28`
- Stability class: `high`
- Canonical source: `db/migrations/0001_init.sql`

## 1. Scope

This schema governs multi-tenant identity, user membership, subscription state, usage event intake, and daily usage reporting.

## 2. Canonical DDL Reference

```sql
create table tenants (
  id uuid primary key,
  slug text not null unique,
  name text not null,
  billing_contact_email text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table users (
  id uuid primary key,
  email text not null unique,
  password_hash text not null,
  global_role text not null default 'user',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table tenant_memberships (
  id uuid primary key,
  tenant_id uuid not null references tenants(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  role text not null,
  created_at timestamptz not null default now(),
  unique (tenant_id, user_id)
);

create table subscriptions (
  id uuid primary key,
  tenant_id uuid not null references tenants(id) on delete restrict,
  plan_code text not null,
  status text not null,
  billing_provider text not null,
  provider_subscription_id text,
  cancel_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  deleted_at timestamptz
);

create table usage_events (
  id uuid primary key,
  tenant_id uuid not null references tenants(id) on delete restrict,
  event_type text not null,
  event_timestamp timestamptz not null,
  quantity integer not null,
  external_event_id text,
  created_at timestamptz not null default now(),
  unique (tenant_id, external_event_id)
);

create table usage_reports (
  id uuid primary key,
  tenant_id uuid not null references tenants(id) on delete restrict,
  report_date date not null,
  total_events integer not null,
  total_quantity bigint not null,
  generated_at timestamptz not null default now(),
  unique (tenant_id, report_date)
);

create index idx_subscriptions_tenant_status on subscriptions(tenant_id, status) where deleted_at is null;
create index idx_usage_events_tenant_timestamp on usage_events(tenant_id, event_timestamp);
create index idx_usage_reports_tenant_date on usage_reports(tenant_id, report_date);
```

## 3. Table Inventory

| Table | Purpose | Soft Delete | Agent May Create/Modify Without Explicit WP? |
|---|---|---|---|
| `tenants` | `Tenant account root entity` | `no` | `no` |
| `users` | `Authenticated principal record` | `no` | `no` |
| `tenant_memberships` | `User-to-tenant role binding` | `no` | `no` |
| `subscriptions` | `Subscription lifecycle state per tenant` | `yes` | `no` |
| `usage_events` | `Tenant-scoped raw usage ingestion` | `no` | `no` |
| `usage_reports` | `Daily aggregated usage per tenant` | `no` | `no` |

## 4. Column Definitions

### Table: `tenants`

| Column | Type | Null? | Default | Constraints | Notes |
|---|---|---|---|---|---|
| `id` | `uuid` | `no` |  | `pk` | `Immutable tenant identifier` |
| `slug` | `text` | `no` |  | `unique` | `Stable human-readable tenant key` |
| `name` | `text` | `no` |  |  | `Display name` |
| `billing_contact_email` | `text` | `yes` |  |  | `PII` |

### Table: `users`

| Column | Type | Null? | Default | Constraints | Notes |
|---|---|---|---|---|---|
| `id` | `uuid` | `no` |  | `pk` | `Immutable user identifier` |
| `email` | `text` | `no` |  | `unique` | `PII, login identity` |
| `password_hash` | `text` | `no` |  |  | `Never expose in API` |
| `global_role` | `text` | `no` | `'user'` |  | `Internal support or normal user` |

### Table: `tenant_memberships`

| Column | Type | Null? | Default | Constraints | Notes |
|---|---|---|---|---|---|
| `id` | `uuid` | `no` |  | `pk` | `Membership identifier` |
| `tenant_id` | `uuid` | `no` |  | `fk -> tenants.id` | `Tenant owner` |
| `user_id` | `uuid` | `no` |  | `fk -> users.id` | `User owner` |
| `role` | `text` | `no` |  |  | `tenant_member, tenant_admin, billing_admin` |

### Table: `subscriptions`

| Column | Type | Null? | Default | Constraints | Notes |
|---|---|---|---|---|---|
| `id` | `uuid` | `no` |  | `pk` | `Subscription identifier` |
| `tenant_id` | `uuid` | `no` |  | `fk -> tenants.id` | `Owner tenant` |
| `plan_code` | `text` | `no` |  |  | `Canonical plan identifier` |
| `status` | `text` | `no` |  |  | `trialing, active, past_due, canceled` |
| `billing_provider` | `text` | `no` |  |  | `stripe initially` |
| `provider_subscription_id` | `text` | `yes` |  |  | `External provider reference` |
| `cancel_at` | `timestamptz` | `yes` |  |  | `Scheduled cancellation time` |
| `deleted_at` | `timestamptz` | `yes` |  |  | `Soft-delete marker` |

### Table: `usage_events`

| Column | Type | Null? | Default | Constraints | Notes |
|---|---|---|---|---|---|
| `id` | `uuid` | `no` |  | `pk` | `Usage event identifier` |
| `tenant_id` | `uuid` | `no` |  | `fk -> tenants.id` | `Owner tenant` |
| `event_type` | `text` | `no` |  |  | `Metered event family` |
| `event_timestamp` | `timestamptz` | `no` |  |  | `When usage occurred` |
| `quantity` | `integer` | `no` |  |  | `Must be positive` |
| `external_event_id` | `text` | `yes` |  | `unique with tenant_id` | `Idempotency key` |

### Table: `usage_reports`

| Column | Type | Null? | Default | Constraints | Notes |
|---|---|---|---|---|---|
| `id` | `uuid` | `no` |  | `pk` | `Report identifier` |
| `tenant_id` | `uuid` | `no` |  | `fk -> tenants.id` | `Owner tenant` |
| `report_date` | `date` | `no` |  | `unique with tenant_id` | `Daily aggregation key` |
| `total_events` | `integer` | `no` |  |  | `Count of source events` |
| `total_quantity` | `bigint` | `no` |  |  | `Summed quantity` |
| `generated_at` | `timestamptz` | `no` | `now()` |  | `Generation time` |

## 5. Index Strategy

| Table | Index Name | Columns | Unique | Reason |
|---|---|---|---|---|
| `subscriptions` | `idx_subscriptions_tenant_status` | `(tenant_id, status)` | `no` | `Tenant-scoped status filtering` |
| `usage_events` | `idx_usage_events_tenant_timestamp` | `(tenant_id, event_timestamp)` | `no` | `Daily usage aggregation scans` |
| `usage_reports` | `idx_usage_reports_tenant_date` | `(tenant_id, report_date)` | `no` | `Fast retrieval of daily report` |

## 6. Relationship Map

| From Table | From Column | To Table | To Column | On Delete | Notes |
|---|---|---|---|---|---|
| `tenant_memberships` | `tenant_id` | `tenants` | `id` | `cascade` | `Membership removed if tenant removed` |
| `tenant_memberships` | `user_id` | `users` | `id` | `cascade` | `Membership removed if user removed` |
| `subscriptions` | `tenant_id` | `tenants` | `id` | `restrict` | `Subscription history preserved intentionally` |
| `usage_events` | `tenant_id` | `tenants` | `id` | `restrict` | `Usage cannot exist without tenant context` |
| `usage_reports` | `tenant_id` | `tenants` | `id` | `restrict` | `Daily report belongs to one tenant` |

## 7. Naming Convention Rules

- Table names are plural snake_case nouns.
- Primary keys are `id`.
- Foreign keys use singular referenced entity plus `_id`.
- Timestamps are `timestamptz` and end with `_at`, except `report_date`.
- External provider identifiers must start with `provider_` or `external_`.

## 8. Soft-Delete Strategy

- Only `subscriptions` is soft-deletable in the current model.
- Soft-deletable entities use `deleted_at timestamptz null`.
- Queries for active subscriptions must exclude soft-deleted rows.

## 9. Audit Column Requirements

- All mutable business tables require `created_at` and `updated_at`.
- Aggregated output tables require `generated_at` if they are derived asynchronously.
- No table in this scope may omit tenancy reference if the data is tenant-owned.

## 10. Protected Fields and Prohibited Agent Actions

- Do not rename `slug`, `email`, `plan_code`, or `provider_subscription_id` without approved CCR.
- Do not add JSON columns for relationships or permissions in this bounded context.
- Do not remove tenant foreign keys.
- Do not create cross-tenant uniqueness rules except where explicitly documented.

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-28` | `OpenAI Codex` | `Initial example` |
