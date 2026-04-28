# Database Schema Constraint Template

> Required fields are marked `[required]`. Optional fields are marked `[optional]`.
> The canonical source of truth is the DDL or migration file referenced below. If no migration exists yet, embed the draft DDL here and treat it as canonical until committed.

## Document Control

- Document ID `[required]`: `schema-core`
- Owner `[required]`: `[backend lead or data owner]`
- Last validated `[required]`: `YYYY-MM-DD`
- Stability class `[required]`: `high`
- Canonical source `[required]`: `db/migrations/0001_init.sql`

## 1. Scope `[required]`

<!-- Name the bounded context covered by this schema constraint. -->
Example:
`Subscription management, tenant identity, and usage reporting tables.`

## 2. Canonical DDL or Migration Reference `[required]`

<!-- If the DDL file exists, link it and copy only the relevant excerpt if needed. If it does not exist, paste the canonical draft here. -->
Example:
```sql
create table tenants (
  id uuid primary key,
  slug text not null unique,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

## 3. Table Inventory `[required]`

| Table | Purpose | Soft Delete | Agent May Create/Modify Without Explicit WP? |
|---|---|---|---|
| `tenants` | `Tenant account root entity` | `no` | `no` |
| `subscriptions` | `Tenant subscription state` | `yes` | `no` |

## 4. Column Definitions `[required]`

<!-- Repeat this section for every governed table. -->
### Table: `subscriptions`

| Column | Type | Null? | Default | Constraints | Notes |
|---|---|---|---|---|---|
| `id` | `uuid` | `no` | `gen_random_uuid()` | `pk` | `Immutable identifier` |
| `tenant_id` | `uuid` | `no` |  | `fk -> tenants.id` | `Tenant owner` |
| `plan_code` | `text` | `no` |  | `check length(plan_code) > 0` | `Provider-neutral plan key` |

## 5. Index Strategy `[required]`

| Table | Index Name | Columns | Unique | Reason |
|---|---|---|---|---|
| `subscriptions` | `idx_subscriptions_tenant_status` | `(tenant_id, status)` | `no` | `Tenant-scoped status lookups` |

## 6. Relationship Map `[required]`

| From Table | From Column | To Table | To Column | On Delete | Notes |
|---|---|---|---|---|---|
| `subscriptions` | `tenant_id` | `tenants` | `id` | `restrict` | `Subscription cannot exist without tenant` |

## 7. Naming Convention Rules `[required]`

<!-- These rules are enforced. -->
Example:
- `Table names are plural snake_case nouns.`
- `Primary keys are always id.`
- `Foreign keys use singular referenced entity plus _id.`
- `Timestamps are timestamptz and end with _at.`

## 8. Soft-Delete Strategy `[required]`

Example:
- `Soft-deleted tables use deleted_at timestamptz nullable column.`
- `Unique indexes on soft-deletable entities must exclude rows where deleted_at is not null.`

## 9. Audit Column Requirements `[required]`

Example:
- `All mutable business tables require created_at and updated_at.`
- `Externally synchronized tables also require source_system and source_updated_at.`

## 10. Protected Fields and Prohibited Agent Actions `[required]`

<!-- List fields the agent must never add, remove, or alter without explicit WP authorization. -->
Example:
- `Do not rename tenant slug fields without approved CCR.`
- `Do not create polymorphic foreign keys.`
- `Do not introduce jsonb columns for relationship data without explicit authorization.`

## 11. Open Questions `[optional]`

Example:
- `Usage aggregation retention window is not finalized.`

## Change Log

| Date | Author | Change |
|---|---|---|
| `YYYY-MM-DD` | `[name]` | `Initial draft` |
