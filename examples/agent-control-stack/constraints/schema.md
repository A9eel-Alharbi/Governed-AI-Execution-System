# Agent Control Stack Schema Constraint

## Document Control

- Document ID: `schema-agent-control-core`
- Owner: `Backend Lead`
- Last validated: `2026-04-29`
- Stability class: `high`
- Canonical source: `examples/agent-control-stack/constraints/schema.md`

## 1. Scope

Persistence for normalized requests, decision traces, case registrations, dispatch outcomes, and execution handoff records.

## 2. Canonical DDL or Migration Reference

```sql
create table requests (
  id uuid primary key,
  raw_input text not null,
  channel text not null,
  actor_id text,
  created_at timestamptz not null default now()
);

create table restoration_traces (
  id uuid primary key,
  request_id uuid not null references requests(id) on delete cascade,
  restored_input text not null,
  trace_json jsonb not null,
  created_at timestamptz not null default now()
);

create table decision_envelopes (
  id uuid primary key,
  request_id uuid not null references requests(id) on delete cascade,
  case_id text,
  policy_decision text not null,
  decision_json jsonb not null,
  created_at timestamptz not null default now()
);

create table case_registrations (
  case_id text primary key,
  status text not null,
  dispatch_target text not null,
  requires_human_review boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table execution_handoffs (
  id uuid primary key,
  decision_envelope_id uuid not null references decision_envelopes(id) on delete cascade,
  handoff_type text not null,
  handoff_target text not null,
  status text not null,
  created_at timestamptz not null default now()
);
```

## 3. Table Inventory

| Table | Purpose | Soft Delete | Agent May Create/Modify Without Explicit WP? |
|---|---|---|---|
| `requests` | `Immutable raw user request intake` | `no` | `no` |
| `restoration_traces` | `Reversible restoration evidence for one request` | `no` | `no` |
| `decision_envelopes` | `Structured clarify/refuse/dispatch/escalate decisions` | `no` | `no` |
| `case_registrations` | `Registered cases and dispatch targets` | `no` | `no` |
| `execution_handoffs` | `Link from approved decision to governed runtime action` | `no` | `no` |

## 4. Column Definitions

### Table: `decision_envelopes`

| Column | Type | Null? | Default | Constraints | Notes |
|---|---|---|---|---|---|
| `id` | `uuid` | `no` |  | `pk` | `Immutable envelope identifier` |
| `request_id` | `uuid` | `no` |  | `fk -> requests.id` | `Source request` |
| `case_id` | `text` | `yes` |  |  | `Present when classification succeeded` |
| `policy_decision` | `text` | `no` |  | `enum: clarify, refuse, dispatch, escalate` | `Top-level outcome` |
| `decision_json` | `jsonb` | `no` |  |  | `Full traceable decision payload` |
| `created_at` | `timestamptz` | `no` | `now()` |  | `Creation timestamp` |

### Table: `case_registrations`

| Column | Type | Null? | Default | Constraints | Notes |
|---|---|---|---|---|---|
| `case_id` | `text` | `no` |  | `pk` | `Stable case identifier` |
| `status` | `text` | `no` |  | `enum: active, deprecated, blocked` | `Registration state` |
| `dispatch_target` | `text` | `no` |  |  | `Procedure, WP path, or onboarding target` |
| `requires_human_review` | `boolean` | `no` | `false` |  | `Pre-dispatch human approval gate` |
| `created_at` | `timestamptz` | `no` | `now()` |  | `Creation timestamp` |
| `updated_at` | `timestamptz` | `no` | `now()` |  | `Last mutation timestamp` |

## 5. Index Strategy

| Table | Index Name | Columns | Unique | Reason |
|---|---|---|---|---|
| `restoration_traces` | `idx_restoration_traces_request_id` | `(request_id)` | `no` | `Fast fetch by request` |
| `decision_envelopes` | `idx_decision_envelopes_request_id` | `(request_id)` | `no` | `One request may have multiple reviewed decisions` |
| `execution_handoffs` | `idx_execution_handoffs_decision_envelope_id` | `(decision_envelope_id)` | `no` | `Audit lookup from decision to execution` |
| `case_registrations` | `idx_case_registrations_status` | `(status)` | `no` | `Registry health and filtering` |

## 6. Relationship Map

| From Table | From Column | To Table | To Column | On Delete | Notes |
|---|---|---|---|---|---|
| `restoration_traces` | `request_id` | `requests` | `id` | `cascade` | `Trace belongs to one request` |
| `decision_envelopes` | `request_id` | `requests` | `id` | `cascade` | `Decision belongs to one request` |
| `execution_handoffs` | `decision_envelope_id` | `decision_envelopes` | `id` | `cascade` | `Handoff belongs to one decision` |

## 7. Naming Convention Rules

- `Table names are plural snake_case nouns.`
- `Primary keys are always id except natural-key registry tables explicitly documented otherwise.`
- `Foreign keys use singular referenced entity plus _id.`
- `Timestamps are timestamptz and end with _at.`

## 8. Soft-Delete Strategy

- `No governed table in phase one uses soft delete.`
- `Historical decision records are immutable and retained through append-only writes.`

## 9. Audit Column Requirements

- `All mutable tables require created_at and updated_at.`
- `Immutable event tables require created_at at minimum.`
- `Decision and trace payloads must remain recoverable from stored jsonb documents.`

## 10. Protected Fields and Prohibited Agent Actions

- `Do not add a silent fallback decision value outside clarify, refuse, dispatch, or escalate without approved CCR.`
- `Do not remove request-to-decision foreign-key lineage.`
- `Do not replace registered case identifiers with ad hoc freeform tool names.`
- `Do not store raw secrets, access tokens, or filesystem contents in decision_json.`

## 11. Open Questions

- `Should trace_json and decision_json be decomposed into relational side tables for analytics in a later phase?`

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-29` | `OpenAI Codex` | `Initial example` |
