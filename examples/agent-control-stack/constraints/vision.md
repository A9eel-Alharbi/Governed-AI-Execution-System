# Agent Control Stack Vision

## Document Control

- Document ID: `vision-agent-control-core`
- Owner: `Product Lead`
- Last validated: `2026-04-29`
- Adoption tier: `Tier 2`

## Product Purpose

This product provides an interpretation-control layer for agentic software systems so teams can turn ambiguous human requests into governed execution decisions instead of letting one opaque model pass silently interpret, normalize, classify, and act.

## Target Users

- `Primary: engineering teams building internal or customer-facing AI agents that can call tools or modify repositories`
- `Primary: platform and security teams that need inspectable agent decisions before execution`
- `Secondary: research and evaluation teams comparing raw tool-calling flows against governed pipelines`

## In Scope

- `Explicit restoration of missing references with reversible trace output`
- `Balancing of aliases, duplicates, and direct contradiction detection`
- `Case classification into registered software-delivery and tool-execution cases`
- `Policy decision layer that returns clarify, refuse, dispatch, or escalate`
- `Dispatch from allowed cases into AOS/CDD onboarding, work-package execution, or change-control paths`
- `Evaluation harness for safe-outcome measurements and avoided model-call tracking`

## Out of Scope

- `General-purpose autonomous planning without registered cases`
- `Silent fallback from unsupported case to generic tool call`
- `Direct execution of destructive file-system or credential actions without explicit protected-resource policy`
- `Model training or foundation-model fine-tuning in phase one`
- `Full multi-tenant hosted control plane in phase one`

## Architecture Direction Decisions

| Decision | Status | Rationale |
|---|---|---|
| `Python packages remain the reference implementation surface` | `approved` | `Existing package work already exists in Python and supports fast iteration` |
| `Decision output is a typed envelope, not freeform prose` | `approved` | `Downstream dispatch and audit require deterministic structure` |
| `AOS/CDD is the governed execution runtime for software-delivery cases` | `approved` | `Execution drift and change-control are already addressed there` |
| `Unsupported and protected cases must fail closed` | `approved` | `The control layer is not credible if unsafe fallbacks remain available` |

## Non-Functional Requirements

- `Deterministic preprocessing overhead under 1 ms p99 for single-request interpretation on local benchmarks`
- `Every decision path emits a trace that identifies restoration, balancing, classification, and dispatch events`
- `Protected-resource cases fail closed when required policy dimensions are absent`
- `The system must support replay of a request from raw input to final decision envelope for audit`

## Questions Not Yet Answered

- `Should the first runtime be library-only, CLI-first, or exposed as an HTTP service immediately?`
- `Which policy dimensions beyond path privilege are mandatory for v1 protected-resource enforcement?`
- `Should AOS/CDD dispatch create work packages automatically or only prepare drafts for human approval?`

## Dependencies and Assumptions

- `Existing jabr, muqabalah, qadiya, and case-eval package concepts remain the base primitives`
- `AOS/CDD artifacts remain repository-local and are not replaced by the interpretation layer`

## Change Log

| Date | Author | Change |
|---|---|---|
| `2026-04-29` | `OpenAI Codex` | `Initial example` |
