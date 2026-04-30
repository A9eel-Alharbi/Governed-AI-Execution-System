"""
Run this script to create the full Governed AI Execution System issue set.

Requirements:
- GitHub CLI installed: https://cli.github.com
- Logged in: gh auth login

Usage:
  python create_issues.py
"""

from __future__ import annotations

import subprocess
import sys
import time

REPO = "A9eel-Alharbi/Governed-AI-Execution-System"


LABELS = [
    ("critical", "e11d48"),
    ("verification", "7c3aed"),
    ("layer-2", "0ea5e9"),
    ("layer-3", "0ea5e9"),
    ("layer-4", "0ea5e9"),
    ("layer-5", "0ea5e9"),
    ("layer-6", "0ea5e9"),
    ("hitl", "f59e0b"),
    ("security", "dc2626"),
    ("dry-run", "10b981"),
    ("policy", "8b5cf6"),
    ("documentation", "6b7280"),
    ("testing", "f97316"),
    ("lock", "ec4899"),
    ("good-first-issue", "22c55e"),
    ("enhancement", "3b82f6"),
    ("robustness", "a16207"),
    ("auth", "0f766e"),
    ("ops", "78716c"),
    ("ci", "166534"),
    ("ui", "be185d"),
    ("session", "4338ca"),
    ("performance", "92400e"),
    ("webhooks", "0369a1"),
    ("concurrency", "b45309"),
    ("known-limitation", "9f1239"),
    ("e2e", "1d4ed8"),
]


ISSUES = [
    {
        "title": "End-to-end: verify one real request travels through all six layers",
        "labels": ["verification", "critical", "good-first-issue", "e2e"],
        "body": """The architecture defines a strictly linear six-layer flow. No shortcuts. No layer jumps. This issue tracks proving that a real request actually travels the full path and produces a real output.

**Acceptance criteria — every checkbox must pass:**
- [ ] User submits a request via UI
- [ ] Layer 2 receives and stores the request
- [ ] Layer 3 classifies it and produces a decision
- [ ] Request pauses at HITL in `PENDING_APPROVAL`
- [ ] Human approves in the UI
- [ ] Layer 4 loads WP, constraints, session, and vault
- [ ] Layer 5 executes within those bounds
- [ ] Layer 6 records the full outcome
- [ ] Result is visible in the UI
- [ ] The full run is retrievable from the audit store

**Reference:** `agent_control_stack/pipeline.py`, `agent_control_stack/executor.py`, `agent_control_stack/store.py`, `platform/api`, `platform/web`""",
    },
    {
        "title": "End-to-end: verify the refusal path terminates cleanly",
        "labels": ["verification", "critical", "e2e"],
        "body": """When Layer 3 classifies a request as `refuse`, execution must terminate immediately. Nothing reaches Layer 4 or Layer 5.

**Acceptance criteria:**
- [ ] Submit a request that clearly violates policy
- [ ] Layer 3 returns `refuse`
- [ ] Layer 4 is never invoked
- [ ] Layer 5 is never invoked
- [ ] User receives a clear refusal reason in the UI
- [ ] Refusal is recorded in Layer 6 audit log
- [ ] Lock is released after refusal

**Reference:** `agent_control_stack/policy.py`, `agent_control_stack/pipeline.py`""",
    },
    {
        "title": "End-to-end: verify the clarify path returns to user correctly",
        "labels": ["verification", "critical", "e2e"],
        "body": """When Layer 3 classifies a request as `clarify`, the system must return a clarification request to the user — not execute, not fail, not hang.

**Acceptance criteria:**
- [ ] Submit an ambiguous request
- [ ] Layer 3 returns `clarify`
- [ ] User receives a clarification prompt in the UI
- [ ] The clarification explains what is missing
- [ ] The original request remains in a re-submittable state
- [ ] Layer 4 and Layer 5 are never invoked
- [ ] Lock is released after clarify response""",
    },
    {
        "title": "End-to-end: verify the escalate path routes correctly",
        "labels": ["verification", "critical", "e2e"],
        "body": """When Layer 3 or the HITL gate escalates a request, it must route to `PENDING_REVIEW` and wait for a higher authority — not execute, not fail.

**Acceptance criteria:**
- [ ] Submit a request that triggers escalation
- [ ] Request enters `PENDING_REVIEW` state
- [ ] Request is visible in an escalation queue in the UI
- [ ] Higher authority can approve or reject from the queue
- [ ] If approved from escalation, execution proceeds normally through Layer 4 and 5
- [ ] If rejected from escalation, request is terminated cleanly
- [ ] Full escalation chain is recorded in Layer 6""",
    },
    {
        "title": "End-to-end: verify the failure path terminates and records correctly",
        "labels": ["verification", "critical", "e2e"],
        "body": """When Layer 5 fails mid-execution, the system must capture everything, set status to `FAILED`, notify the user, and release the lock.

**Acceptance criteria:**
- [ ] Trigger an execution failure in Layer 5
- [ ] Status is set to `FAILED`
- [ ] Error and stack trace are captured
- [ ] Last successful step is recorded
- [ ] Partial artifacts are stored
- [ ] Full tool call log is stored
- [ ] User sees failure summary in UI with trace link
- [ ] Re-submit option is available
- [ ] Lock is released
- [ ] Layer 6 audit record is complete""",
    },
    {
        "title": "End-to-end: verify dry-run produces a trace without any writes",
        "labels": ["verification", "critical", "dry-run", "e2e"],
        "body": """A dry-run request must travel through all six layers, execute full logic, and produce a complete trace — with zero actual writes to the repo or any external system.

**Acceptance criteria:**
- [ ] User selects dry-run toggle in UI before submitting
- [ ] Request travels through all six layers normally
- [ ] HITL gate still activates — dry-run does not skip approval
- [ ] Layer 5 executes full logic
- [ ] Zero writes are committed anywhere
- [ ] Skipped writes log is populated
- [ ] Draft artifacts exist but are not committed
- [ ] Execution trace is complete
- [ ] Summary says "X would have changed, Y would have been created"
- [ ] Layer 6 records the dry-run run separately from live runs""",
    },
    {
        "title": "Layer 2: verify request record is created before forwarding to Layer 3",
        "labels": ["layer-2", "verification"],
        "body": """Layer 2 must create a persistent request record before forwarding to Layer 3. If Layer 3 fails, the request must still exist in Layer 2's store.

**Acceptance criteria:**
- [ ] Submit a request
- [ ] Verify the request record exists in the DB before Layer 3 responds
- [ ] Verify the record contains: request text, user, project, timestamp, initial status
- [ ] Verify a Layer 3 failure does not delete the request record""",
    },
    {
        "title": "Layer 2: verify auth enforces project-level access control",
        "labels": ["layer-2", "security", "auth"],
        "body": """Every API endpoint in Layer 2 must verify the requesting user has access to the specific project they are acting on.

**Acceptance criteria:**
- [ ] User A cannot read Project B's requests
- [ ] User A cannot read Project B's policy profiles
- [ ] User A cannot read Project B's run history
- [ ] User A cannot submit requests to Project B
- [ ] User A cannot approve Project B's HITL queue items
- [ ] Every API endpoint has an authorization check

**Reference:** `platform/api/app`""",
    },
    {
        "title": "Layer 2: verify repo connection metadata is stored and retrievable",
        "labels": ["layer-2", "verification"],
        "body": """Layer 2 stores repo connection metadata. Layer 4 depends on this to load WPs, constraints, and sessions.

**Acceptance criteria:**
- [ ] Connect a repo through the UI
- [ ] Verify metadata is stored: repo URL, auth token reference, branch, root path
- [ ] Verify Layer 4 can retrieve the connection and use it
- [ ] Verify disconnecting a repo is reflected in subsequent Layer 4 attempts""",
    },
    {
        "title": "Layer 2: verify UI↔repo sync state is accurate and surfaced in the UI",
        "labels": ["layer-2", "verification", "ui"],
        "body": """Layer 2 is responsible for sync between UI state and repo artifacts. Users should know if what they see in the UI matches what is in the repo.

**Acceptance criteria:**
- [ ] After a successful execution, repo artifacts match UI-visible state
- [ ] If a repo artifact changes externally, the UI reflects or flags the mismatch
- [ ] Sync status is visible somewhere in the UI
- [ ] A failed sync does not silently corrupt state""",
    },
    {
        "title": "Layer 2: verify API token storage uses a vault reference — never plaintext",
        "labels": ["layer-2", "security"],
        "body": """API tokens for repo connections must never be stored as plaintext in the database.

**Acceptance criteria:**
- [ ] Inspect the DB record for a connected repo — no plaintext token exists
- [ ] Token reference points to the vault
- [ ] Token is retrieved from vault at execution time, not stored in Layer 2
- [ ] A leaked DB dump does not expose any usable tokens""",
    },
    {
        "title": "Layer 3: verify normalization runs before classification",
        "labels": ["layer-3", "verification", "critical"],
        "body": """The spec defines Layer 3 as: restore context → normalize/balance → classify → apply policy. This issue verifies the normalization step actually runs.

**Acceptance criteria:**
- [ ] Submit a request with inconsistent casing, extra whitespace, or ambiguous phrasing
- [ ] Verify normalization transforms the input before classification
- [ ] Verify the classification is based on the normalized input, not the raw input
- [ ] Verify the original raw input is still stored in the audit record unchanged

**Reference:** `agent_control_stack/pipeline.py`""",
    },
    {
        "title": "Layer 3: verify context restoration uses the correct project context",
        "labels": ["layer-3", "verification", "session", "critical"],
        "body": """Layer 3 restores context before processing. This must use the correct project's context — not a stale context, not another project's context.

**Acceptance criteria:**
- [ ] Submit a request for Project A — verify context is Project A's
- [ ] Submit a request for Project B — verify context is Project B's
- [ ] Verify context includes: project vision, constraints, policy profile, previous session state
- [ ] Verify what happens when context is missing — clarify, fail, or use defaults?
- [ ] Verify stale context from a failed previous run does not pollute the next run

**Reference:** `agent_control_stack/pipeline.py`""",
    },
    {
        "title": "Layer 3: verify all four decision outcomes are reachable and tested",
        "labels": ["layer-3", "verification", "critical"],
        "body": """Layer 3 must be capable of producing all four outcomes: `clarify`, `refuse`, `dispatch`, `escalate`.

**Acceptance criteria:**
- [ ] `clarify` — submit an ambiguous request, verify clarify is returned
- [ ] `refuse` — submit a policy-violating request, verify refuse is returned
- [ ] `dispatch` — submit a valid request, verify dispatch is returned
- [ ] `escalate` — submit a request that exceeds authority, verify escalate is returned
- [ ] Each outcome produces the correct downstream behavior
- [ ] Each outcome is recorded in Layer 6

**Reference:** `agent_control_stack/pipeline.py`, `agent_control_stack/runtime/case_registry.yaml`""",
    },
    {
        "title": "Layer 3: document and expand the case registry",
        "labels": ["layer-3", "documentation", "enhancement"],
        "body": """`case_registry.yaml` defines known case families. This issue tracks documenting what each case means, expanding coverage, and defining what happens for unknown cases.

**Current supported cases:**
- `new_project.initial_definition`
- `implementation.create_first_wp`
- `implementation.run_wp`
- `implementation.review_wp`
- `implementation.create_followup_wp`
- `change.constraint_conflict`
- `docs.update_constraints`
- `ops.run_validation`
- `security.protected_resource_change`

**What needs to be done:**
- [ ] Document what each case family means and when it triggers
- [ ] Define what happens for unrecognized cases — clarify or refuse?
- [ ] Add test requests that should trigger each case
- [ ] Identify missing case families from real usage
- [ ] Add missing cases to the registry

**Reference:** `agent_control_stack/runtime/case_registry.yaml`""",
    },
    {
        "title": "Layer 3: document the policy profile format completely",
        "labels": ["layer-3", "documentation", "policy"],
        "body": """Apply policy appears throughout the spec but what a policy profile actually looks like — its schema, fields, valid values — is not documented.

**What needs to be done:**
- [ ] Document the full policy profile schema with every field
- [ ] Provide a minimal working example policy profile
- [ ] Explain what each field controls — what it blocks, allows, escalates
- [ ] Document who should write policies
- [ ] Add a policy authoring guide to `docs/`
- [ ] Add at least three example policies to `examples/` — strict, moderate, permissive

**Reference:** `agent_control_stack/policy.py`, `machine/`""",
    },
    {
        "title": "Layer 3: verify policy approval-artifact overlays work correctly",
        "labels": ["layer-3", "verification", "policy"],
        "body": """The spec states Layer 3 applies "approval-artifact policy overlays." This issue verifies that overlay logic works correctly.

**Acceptance criteria:**
- [ ] Document what an approval-artifact overlay is and when it applies
- [ ] Verify overlays are applied after base policy, not instead of it
- [ ] Verify overlays are visible in the audit record
- [ ] Verify removing an overlay reverts to base policy behavior""",
    },
    {
        "title": "Layer 3: define and test behavior for unknown or malformed requests",
        "labels": ["layer-3", "verification", "robustness"],
        "body": """What does Layer 3 do when it receives a request it cannot parse, classify, or normalize? This must be defined and tested.

**Acceptance criteria:**
- [ ] Submit an empty request — verify correct response
- [ ] Submit a request with only special characters — verify correct response
- [ ] Submit a very long request exceeding expected limits — verify correct response
- [ ] Submit a request in an unexpected language — verify correct response
- [ ] None of the above should crash Layer 3 or leave the lock held""",
    },
    {
        "title": "HITL: verify gate actually blocks execution — not just updates status",
        "labels": ["hitl", "verification", "critical"],
        "body": """The HITL gate must physically prevent Layer 4 from being invoked while a request is in `PENDING_APPROVAL`. Updating a status field while execution continues is not acceptable.

**Acceptance criteria:**
- [ ] Submit a dispatchable request
- [ ] Verify Layer 4 is NOT called while status is `PENDING_APPROVAL`
- [ ] Verify Layer 5 is NOT called while status is `PENDING_APPROVAL`
- [ ] Approve the request
- [ ] Verify Layer 4 IS called after approval
- [ ] Reject the request on a separate test — verify Layer 4 is never called

**Reference:** `platform/api/app`""",
    },
    {
        "title": "HITL: verify TTL expiry releases lock and marks request FAILED",
        "labels": ["hitl", "verification", "critical", "lock"],
        "body": """If a request sits in `PENDING_APPROVAL` beyond the defined TTL, it must auto-expire — releasing the lock and marking the request as `FAILED`.

**Acceptance criteria:**
- [ ] Set a short TTL for testing purposes
- [ ] Submit a request and do not approve it
- [ ] Wait for TTL to expire
- [ ] Verify status changes to `FAILED`
- [ ] Verify lock is released — new requests can be submitted
- [ ] Verify user is notified of expiry
- [ ] Verify expiry is recorded in Layer 6""",
    },
    {
        "title": "HITL: verify all six states are reachable and transition correctly",
        "labels": ["hitl", "verification"],
        "body": """The state machine defines six states. Every state must be reachable and every transition must be verified.

**States:**
```
SUBMITTED → CLASSIFIED → PENDING_APPROVAL → APPROVED → DISPATCHED
                                          ↓
                                        REJECTED → TERMINATED
                                          ↓
                                        ESCALATED → PENDING_REVIEW
```

**Acceptance criteria:**
- [ ] `SUBMITTED` — request is created
- [ ] `CLASSIFIED` — Layer 3 has processed it
- [ ] `PENDING_APPROVAL` — waiting at HITL gate
- [ ] `APPROVED` → `DISPATCHED` — human approved, Layer 4 invoked
- [ ] `REJECTED` → `TERMINATED` — human rejected, nothing executes
- [ ] `ESCALATED` → `PENDING_REVIEW` — routes to higher authority
- [ ] Every transition is recorded with timestamp in Layer 6""",
    },
    {
        "title": "HITL: verify the approval UI shows all required information",
        "labels": ["hitl", "ui", "verification"],
        "body": """The spec defines exactly what the HITL approval UI must show. This issue verifies every required element is present.

**Required elements:**
- [ ] Request summary in plain language
- [ ] Intended actions list — what Layer 4 would do
- [ ] Risk level indicator — low / medium / high
- [ ] Policy rules that were triggered
- [ ] Three action buttons: Approve · Reject · Escalate
- [ ] Requesting user and project context
- [ ] Timestamp and TTL countdown

**Reference:** Approval queue UI in `platform/web`""",
    },
    {
        "title": "HITL: verify stored PENDING_APPROVAL record contains all required fields",
        "labels": ["hitl", "verification"],
        "body": """Every field defined in the spec must be present in the stored record.

**Required fields:**
- [ ] `request_text` — original request exactly as submitted
- [ ] `policy_decision` — classification and risk level from Layer 3
- [ ] `intended_actions` — what Layer 4 would execute
- [ ] `project_context` — requesting user, project, timestamp
- [ ] `expires_at` — TTL value""",
    },
    {
        "title": "Layer 4: verify it is never invoked without prior HITL approval",
        "labels": ["layer-4", "verification", "critical", "security"],
        "body": """Layer 4 must only be reachable after a request has been explicitly approved at the HITL gate. Any path that reaches Layer 4 without a recorded HITL approval is a critical security failure.

**Acceptance criteria:**
- [ ] Attempt to invoke Layer 4 directly via API — must be rejected
- [ ] Verify every Layer 4 invocation has a corresponding HITL approval record in Layer 6
- [ ] A request without a HITL record must not proceed to Layer 4 under any circumstances

**Reference:** `agent_control_stack/executor.py` — `GovernedExecutionPlanner`""",
    },
    {
        "title": "Layer 4: verify vault health check blocks execution when vault is unhealthy",
        "labels": ["layer-4", "verification", "security"],
        "body": """Layer 4 checks vault health before proceeding. An unhealthy vault must block execution — not produce a warning and continue.

**Acceptance criteria:**
- [ ] Define what "unhealthy vault" means — unavailable, timeout, wrong state
- [ ] Simulate an unhealthy vault
- [ ] Verify Layer 4 does not proceed to Layer 5
- [ ] Verify the failure is captured in Layer 6
- [ ] Verify the lock is released
- [ ] Verify the user is notified with a clear message
- [ ] Document how to run without a vault for development

**Reference:** `agent_control_stack/executor.py` — `GovernedExecutionPlanner`""",
    },
    {
        "title": "Layer 4: verify repo-root path safety blocks all boundary escapes",
        "labels": ["layer-4", "security", "verification"],
        "body": """Layer 4 enforces repo-root path safety. No execution should be able to write outside the defined repo root.

**Acceptance criteria:**
- [ ] Attempt a write to a path outside the repo root — must be blocked
- [ ] Attempt a path traversal (`../`) — must be blocked
- [ ] Attempt an absolute path outside the repo root — must be blocked
- [ ] Attempt a symlink that points outside the repo root — must be blocked
- [ ] All blocked attempts are recorded in Layer 6""",
    },
    {
        "title": "Layer 4: document and verify change-control routing logic",
        "labels": ["layer-4", "verification", "documentation"],
        "body": """The spec states Layer 4 "routes through change-control if needed." This issue tracks defining when CCR routing triggers and verifying it works.

**What needs to be done:**
- [ ] Document what triggers CCR routing — which request types, which risk levels
- [ ] Document what CCR routing means in practice — what happens, who is notified
- [ ] Verify CCR routing works when triggered
- [ ] Verify CCR routing does not activate for requests that should not trigger it
- [ ] Add CCR routing to the audit record

**Reference:** `agent_control_stack/executor.py` — `GovernedExecutionPlanner`""",
    },
    {
        "title": "Layer 4: verify missing or malformed WP fails safely",
        "labels": ["layer-4", "verification", "robustness"],
        "body": """If the WP is missing, malformed, or incompatible with constraints, Layer 4 must fail safely — not proceed with a broken WP.

**Acceptance criteria:**
- [ ] Attempt execution with a missing WP — must fail before reaching Layer 5
- [ ] Attempt execution with a malformed WP — must fail before reaching Layer 5
- [ ] Attempt execution with a WP that conflicts with constraints — must fail
- [ ] All failures are recorded in Layer 6 with clear error messages
- [ ] Lock is released on all failure cases""",
    },
    {
        "title": "Layer 4: verify dry-run flag is correctly set in the execution context",
        "labels": ["layer-4", "dry-run", "verification"],
        "body": """Layer 4 is responsible for setting `mode = DRY_RUN` in the execution context. This issue verifies the flag is correctly present before Layer 5 is invoked.

**Acceptance criteria:**
- [ ] Submit a dry-run request
- [ ] Verify `mode = DRY_RUN` is present in the execution context Layer 5 receives
- [ ] Submit a live request
- [ ] Verify `mode = DRY_RUN` is NOT present in the execution context Layer 5 receives""",
    },
    {
        "title": "Layer 5: enforce explicit write declaration for all tools",
        "labels": ["layer-5", "dry-run", "critical"],
        "body": """The dry-run contract requires every tool to explicitly declare write capability. Without enforcement, a new tool can silently write during dry-run.

**What needs to be done:**
- [ ] Define the write capability declaration format
- [ ] Add a registry or decorator for tools to declare write operations
- [ ] Add enforcement at execution time — undeclared writes are blocked
- [ ] Add a test: a tool without a declaration cannot write anything
- [ ] Document the declaration requirement in CONTRIBUTING.md
- [ ] Audit all existing tools — verify every write is declared

**Reference:** `agent_control_stack/executor.py` — `GovernedExecutor`""",
    },
    {
        "title": "Layer 5: verify model execution cannot exceed bounds defined by Layer 4",
        "labels": ["layer-5", "verification", "critical", "security"],
        "body": """Layer 5 must only execute what Layer 4 defined as allowed. The model must not be able to extend its own scope or invoke undeclared tools.

**Acceptance criteria:**
- [ ] Attempt to invoke a tool not listed in the Layer 4 execution context — must be blocked
- [ ] Attempt to read a file outside the repo root — must be blocked
- [ ] Attempt to write to a path not declared — must be blocked
- [ ] All blocked attempts are recorded in Layer 6""",
    },
    {
        "title": "Layer 5: define and verify completion evidence format",
        "labels": ["layer-5", "verification", "documentation"],
        "body": """Layer 5 produces "completion evidence" for every successful execution. The format is not yet defined.

**What needs to be done:**
- [ ] Define the completion evidence schema
- [ ] Verify evidence is produced for every successful execution
- [ ] Verify partial evidence is captured for failed executions
- [ ] Verify evidence is stored in Layer 6
- [ ] Document the evidence format in `docs/`
- [ ] Add evidence validation to the CI check""",
    },
    {
        "title": "Layer 5: verify dry-run mode skips all writes across all tools",
        "labels": ["layer-5", "dry-run", "verification"],
        "body": """Every tool in Layer 5 must skip write operations when `mode = DRY_RUN`.

**Acceptance criteria:**
- [ ] Run every supported tool in dry-run mode
- [ ] Verify zero files are written or committed
- [ ] Verify every skipped write is in the skipped writes log
- [ ] Verify draft artifacts exist but are not committed
- [ ] Verify a new tool added without dry-run handling defaults to read-only""",
    },
    {
        "title": "Layer 5: verify tool call log captures every invocation in order",
        "labels": ["layer-5", "verification", "ops"],
        "body": """The tool call log must capture every tool Layer 5 invokes, in order, with inputs and outputs.

**Acceptance criteria:**
- [ ] Run a multi-step execution
- [ ] Verify the tool call log shows every tool in the correct order
- [ ] Verify each entry contains: tool name, inputs, output, timestamp, success/failure
- [ ] Verify the log is complete even for partial executions that failed midway""",
    },
    {
        "title": "Layer 6: verify audit record is complete for every execution path",
        "labels": ["layer-6", "verification", "critical"],
        "body": """Every request path must produce a complete audit record.

**Required fields for every record:**
- [ ] Original request text
- [ ] Classification decision and reasoning
- [ ] Policy rules applied
- [ ] HITL decision and who made it
- [ ] Execution trace — all Layer 5 steps
- [ ] Write operations or skipped writes
- [ ] Completion evidence or failure trace
- [ ] Final status and timestamp

**Verify for every path:**
- [ ] Successful execution
- [ ] Refused at Layer 3
- [ ] Clarify response
- [ ] Rejected at HITL
- [ ] Escalated at HITL
- [ ] Execution failure
- [ ] Dry-run execution
- [ ] Stuck lock auto-release
- [ ] TTL expiry

**Reference:** `agent_control_stack/store.py`""",
    },
    {
        "title": "Layer 6: implement webhooks / alert side-channel",
        "labels": ["layer-6", "webhooks", "enhancement"],
        "body": """The architecture diagram shows a webhooks/alert side-channel off Layer 6. This is not yet implemented.

**What needs to be done:**
- [ ] Define the webhook payload format
- [ ] Implement webhook delivery on: execution complete, execution failed, HITL escalation, TTL expiry
- [ ] Add webhook URL configuration to project settings in the UI
- [ ] Implement retry logic for failed webhook deliveries
- [ ] Add webhook delivery records to the Layer 6 audit store
- [ ] Document the webhook format in `docs/api.md`""",
    },
    {
        "title": "Layer 6: verify policy feedback loop surfaces all required data to the dashboard",
        "labels": ["layer-6", "policy", "verification"],
        "body": """The policy feedback loop depends on Layer 6 surfacing specific data to the dashboard.

**Required data:**
- [ ] Execution results — success and failure counts
- [ ] Policy violations — which rules triggered and how often
- [ ] HITL decisions — approve / reject / escalate breakdown
- [ ] Decision traces — why Layer 3 classified each request
- [ ] Failure traces — where execution broke down

**Acceptance criteria:**
- [ ] Run 10 requests with a mix of outcomes
- [ ] Open the policy dashboard
- [ ] Verify all five data types are present and accurate""",
    },
    {
        "title": "Layer 6: verify ops report output matches actual execution data",
        "labels": ["layer-6", "verification", "ops"],
        "body": """The ops report must accurately reflect what happened.

**Acceptance criteria:**
- [ ] Run 10 requests with mixed outcomes
- [ ] Run `python -m agent_control_stack.ops_report --store-dir runs`
- [ ] Verify failure count matches actual failures
- [ ] Verify refusal count matches actual refusals
- [ ] Verify HITL decision counts are accurate
- [ ] Verify dry-run executions are separate from live executions
- [ ] Verify policy violation count is accurate

**Reference:** `agent_control_stack/ops_report.py`""",
    },
    {
        "title": "Layer 6: verify CI validation enforces policy-aware checks",
        "labels": ["layer-6", "ci", "verification"],
        "body": """The CI workflow enforces policy-aware checks. This issue verifies those checks actually fail on real violations.

**Acceptance criteria:**
- [ ] Introduce a deliberate policy violation into the repo
- [ ] Verify CI fails with a clear error message
- [ ] Verify CI passes after the violation is corrected
- [ ] Verify the CI check output is human-readable
- [ ] Verify CI validation results are included in the audit report

**Reference:** `.github/workflows/aos-validate.yml`, `agent_control_stack/policy_gate.py`""",
    },
    {
        "title": "Layer 6: implement data retention policy",
        "labels": ["layer-6", "enhancement", "ops"],
        "body": """The spec lists "retention" as a Layer 6 responsibility. No retention policy is currently defined or implemented.

**What needs to be done:**
- [ ] Define how long run records are retained by default
- [ ] Implement a configurable retention period
- [ ] Implement a cleanup job that removes expired records
- [ ] Ensure cleanup never removes records within their retention window
- [ ] Document the retention policy in `docs/`""",
    },
    {
        "title": "Lock: verify it prevents concurrent request submission",
        "labels": ["lock", "verification", "critical", "concurrency"],
        "body": """The `is_processing` lock must physically prevent a second request from being submitted while one is active.

**Acceptance criteria:**
- [ ] Submit a request — lock becomes `true`
- [ ] Attempt to submit a second request while lock is `true` — must be rejected
- [ ] UI submit button is disabled while lock is `true`
- [ ] API endpoint returns an appropriate error if a second request is submitted directly
- [ ] Lock returns to `false` after completion or failure""",
    },
    {
        "title": "Lock: verify stuck lock auto-releases after timeout",
        "labels": ["lock", "verification", "critical"],
        "body": """If `is_processing` remains `true` beyond the defined timeout, the system must auto-release the lock and mark the request as `FAILED`.

**Acceptance criteria:**
- [ ] Set a short timeout for testing
- [ ] Simulate a stuck execution — lock stays `true`
- [ ] Wait for timeout
- [ ] Verify lock returns to `false`
- [ ] Verify request is marked `FAILED`
- [ ] Verify user is notified
- [ ] Verify the timeout event is recorded in Layer 6""",
    },
    {
        "title": "Lock: verify manual force-unlock works and is access-controlled",
        "labels": ["lock", "verification", "security", "ui"],
        "body": """A manual force-unlock button must exist in the UI. It must be access-controlled — not available to all users.

**Acceptance criteria:**
- [ ] Force-unlock button exists in the UI
- [ ] Force-unlock releases the lock immediately
- [ ] Force-unlock marks the request as `FAILED`
- [ ] Force-unlock is only available to authorized users
- [ ] Force-unlock event is recorded in Layer 6 with who did it and when""",
    },
    {
        "title": "Security: verify tenant isolation — Project A cannot access Project B",
        "labels": ["security", "critical", "verification"],
        "body": """Every project's data must be physically isolated from every other project.

**Acceptance criteria:**
- [ ] Project A's policy profile is not readable by Project B's requests
- [ ] Project A's execution history is not visible to Project B's users
- [ ] Project A's repo connection cannot be used by Project B
- [ ] API endpoints enforce project-level authorization on every request
- [ ] HITL queue for Project A is not visible to Project B's users
- [ ] Lock state for Project A is independent of Project B's lock state""",
    },
    {
        "title": "Security: verify API tokens never appear as plaintext in any output",
        "labels": ["security", "verification"],
        "body": """API tokens must never appear in plaintext in any log, audit record, API response, or error message.

**Acceptance criteria:**
- [ ] Inspect every audit record — no plaintext tokens
- [ ] Inspect every API response — no plaintext tokens
- [ ] Trigger a vault error — verify error message contains no token
- [ ] Inspect Layer 5 tool call logs — no plaintext tokens
- [ ] Inspect ops report output — no plaintext tokens""",
    },
    {
        "title": "Security: verify path traversal is blocked at every write point",
        "labels": ["security", "verification"],
        "body": """Path traversal attacks must be blocked at every point where a path is constructed for writing.

**Acceptance criteria:**
- [ ] Test `../` traversal at Layer 4 — must be blocked
- [ ] Test absolute paths at Layer 4 — must be blocked
- [ ] Test `../` in tool write declarations at Layer 5 — must be blocked
- [ ] Test symlinks that escape the repo root — must be blocked
- [ ] All blocked attempts are logged""",
    },
    {
        "title": "Security: write a threat model for the governed execution system",
        "labels": ["security", "documentation"],
        "body": """A threat model does not exist. Without it, contributors do not know what the system is designed to protect against.

**What needs to be done:**
- [ ] Define the trust boundaries — what is trusted, what is not
- [ ] Define the attack surface — which layers are exposed, which are internal
- [ ] Define the known threats and how the architecture mitigates them
- [ ] Define what the system explicitly does NOT protect against
- [ ] Add the threat model to `docs/`""",
    },
    {
        "title": "Policy: implement writeback of policy edits to repo artifacts",
        "labels": ["policy", "known-limitation", "enhancement"],
        "body": """**This is a documented known limitation from the README.**

Policy edits made in the UI are versioned in the platform database but not written back to the connected repo as artifacts.

**What needs to be done:**
- [ ] When a policy profile is saved in the UI, trigger a write to the repo
- [ ] The write goes through change-control — not a direct commit
- [ ] Repo artifact matches the platform version exactly
- [ ] A mismatch between platform and repo policy is surfaced as a warning in the UI
- [ ] Add a sync status indicator to the policy UI
- [ ] Add a sync test to the CI check

**Reference:** `agent_control_stack/policy.py`, `platform/api/app`""",
    },
    {
        "title": "Policy: verify versioning captures all required fields",
        "labels": ["policy", "verification"],
        "body": """Every policy change must be stored as a versioned record with all required fields.

**Required fields:**
- `previous_state` — full snapshot before the change
- `new_state` — full snapshot after the change
- `changed_by` — user who made the change
- `changed_at` — timestamp
- `reason` — free text, required, cannot be blank

**Acceptance criteria:**
- [ ] Edit a policy profile
- [ ] Verify all five fields exist in the version record
- [ ] Attempt to save a policy change with no reason — must be rejected
- [ ] Verify previous and new state are full snapshots, not diffs""",
    },
    {
        "title": "Policy: verify version history is visible in the UI",
        "labels": ["policy", "ui", "verification"],
        "body": """Users must be able to see the full version history of any policy profile.

**Acceptance criteria:**
- [ ] Make three edits to a policy profile
- [ ] Open the policy version history in the UI
- [ ] Verify all three versions are listed with author, timestamp, and reason
- [ ] Verify the previous state is viewable for each version""",
    },
    {
        "title": "Docs: verify QUICKSTART.md works on a clean environment",
        "labels": ["documentation", "verification", "good-first-issue"],
        "body": """A new contributor should be able to follow QUICKSTART.md from zero and end up with a working governed request. Every command must work exactly as written.

**Acceptance criteria:**
- [ ] Follow QUICKSTART.md on a clean machine with no prior setup
- [ ] Every command runs without modification
- [ ] The example request completes end to end
- [ ] Output matches what the quickstart says it will produce
- [ ] Any gaps or errors found are fixed in the doc immediately

**Reference:** `QUICKSTART.md`""",
    },
    {
        "title": "Docs: add a complete worked example with full artifact trail",
        "labels": ["documentation", "enhancement"],
        "body": """The `examples/` directory needs a complete worked example showing one full governed request from submission to audit record.

**The example must include:**
- [ ] The request text
- [ ] The classification decision and reasoning
- [ ] The HITL approval record
- [ ] The WP and constraints loaded by Layer 4
- [ ] The execution trace from Layer 5
- [ ] The completion evidence
- [ ] The full audit record from Layer 6""",
    },
    {
        "title": "Docs: add sequence diagram for the full request lifecycle",
        "labels": ["documentation"],
        "body": """`docs/architecture.md` describes the layers but does not show the exact lifecycle of a request as a sequence diagram.

**The diagram must show:**
- [ ] Request submission
- [ ] Layer 3 classification — all four outcomes
- [ ] HITL gate — all three decisions
- [ ] Layer 4 execution planning
- [ ] Layer 5 execution
- [ ] Failure path
- [ ] Dry-run path
- [ ] Layer 6 audit record
- [ ] Result return to UI""",
    },
    {
        "title": "Docs: document all environment variables and configuration options",
        "labels": ["documentation"],
        "body": """There is no single place that documents all environment variables, configuration files, and their valid values.

**What needs to be done:**
- [ ] List every environment variable the system uses
- [ ] Document the default value and valid range for each
- [ ] Document which variables are required vs optional
- [ ] Document which variables are sensitive
- [ ] Add this to `docs/` and reference it from the README""",
    },
    {
        "title": "Docs: complete the deployment guide for self-hosted production use",
        "labels": ["documentation"],
        "body": """The deployment guide may not cover everything needed to run this in a real self-hosted environment.

**What needs to be covered:**
- [ ] System requirements — OS, Python version, Node version
- [ ] Database setup and schema migration
- [ ] Vault setup and connection
- [ ] Repo connection configuration
- [ ] Auth setup
- [ ] Running platform API in production
- [ ] Running the web UI in production
- [ ] Running the agent control stack
- [ ] Health checks and monitoring
- [ ] Backup and recovery

**Reference:** `docs/deployment.md`""",
    },
    {
        "title": "Tests: add integration tests for every HITL state transition",
        "labels": ["testing", "hitl"],
        "body": """Every HITL state transition must have an integration test.

**Tests needed:**
- [ ] `PENDING_APPROVAL` → `APPROVED` → `DISPATCHED`
- [ ] `PENDING_APPROVAL` → `REJECTED` → `TERMINATED`
- [ ] `PENDING_APPROVAL` → `ESCALATED` → `PENDING_REVIEW`
- [ ] `PENDING_APPROVAL` → TTL expiry → `FAILED`
- [ ] `PENDING_REVIEW` → approved → `DISPATCHED`
- [ ] `PENDING_REVIEW` → rejected → `TERMINATED`

**Reference:** `tests/`""",
    },
    {
        "title": "Tests: add regression tests for all documented non-goals",
        "labels": ["testing"],
        "body": """Non-goals are as binding as goals. These tests fail if a non-goal is accidentally implemented.

**Non-goals to test:**
- [ ] No auto-approval at HITL based on risk score
- [ ] No automatic repo revert on failure
- [ ] No retry logic on execution failure
- [ ] No partial dry-run
- [ ] No automatic policy mutation
- [ ] No model influence on HITL decision
- [ ] No write without explicit declaration in Layer 5""",
    },
    {
        "title": "Tests: add scenario tests for all nine supported case families",
        "labels": ["testing", "layer-3"],
        "body": """Every case family in the case registry must have at least one scenario test.

**Cases to cover:**
- [ ] `new_project.initial_definition`
- [ ] `implementation.create_first_wp`
- [ ] `implementation.run_wp`
- [ ] `implementation.review_wp`
- [ ] `implementation.create_followup_wp`
- [ ] `change.constraint_conflict`
- [ ] `docs.update_constraints`
- [ ] `ops.run_validation`
- [ ] `security.protected_resource_change`""",
    },
    {
        "title": "Tests: add performance baseline for end-to-end request latency",
        "labels": ["testing", "performance"],
        "body": """There is no defined acceptable latency for a request traveling through all six layers. Without a baseline, performance regressions are invisible.

**What needs to be done:**
- [ ] Measure end-to-end latency for a standard request (excluding HITL wait time)
- [ ] Break down latency by layer
- [ ] Define acceptable latency thresholds
- [ ] Add a performance test that fails if thresholds are exceeded
- [ ] Document the baseline in `docs/`""",
    },
    {
        "title": "Tests: add test for unknown case classification behavior",
        "labels": ["testing", "layer-3", "robustness"],
        "body": """When a request matches no known case in the case registry, the system must have defined behavior.

**Acceptance criteria:**
- [ ] Submit a request that matches no known case
- [ ] Verify the system returns `clarify` or `refuse` — not an unhandled error
- [ ] Verify the response is user-readable
- [ ] Verify the event is recorded in Layer 6""",
    },
]

EXPECTED_ISSUE_COUNT = 60


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")


def require_gh_auth() -> None:
    version = run(["gh", "--version"])
    if version.returncode != 0:
        print("GitHub CLI is not installed or not available on PATH.")
        print(version.stderr.strip() or version.stdout.strip())
        sys.exit(1)

    auth = run(["gh", "auth", "status"])
    if auth.returncode != 0:
        print("GitHub CLI is installed, but you are not authenticated.")
        print(auth.stderr.strip() or auth.stdout.strip())
        sys.exit(1)


def create_labels() -> None:
    print("Creating labels...")
    for name, color in LABELS:
        result = run(
            [
                "gh",
                "label",
                "create",
                name,
                "--color",
                color,
                "--repo",
                REPO,
                "--force",
            ]
        )
        ok = result.returncode == 0
        if not ok:
            print(f"  ⚠ {result.stderr.strip() or result.stdout.strip()}")
        print(f"  {'✓' if ok else '✗'} {name}")


def create_issues() -> None:
    print(f"\nCreating {len(ISSUES)} issues...")
    for i, issue in enumerate(ISSUES, 1):
        result = run(
            [
                "gh",
                "issue",
                "create",
                "--title",
                issue["title"],
                "--body",
                issue["body"],
                "--label",
                ",".join(issue["labels"]),
                "--repo",
                REPO,
            ]
        )
        ok = result.returncode == 0
        if not ok:
            print(f"  ⚠ {result.stderr.strip() or result.stdout.strip()}")
        print(f"  {'✓' if ok else '✗'} [{i:02d}/{len(ISSUES)}] {issue['title'][:70]}")
        time.sleep(0.5)


def main() -> None:
    if len(ISSUES) != EXPECTED_ISSUE_COUNT:
        print(
            f"Issue count mismatch: expected {EXPECTED_ISSUE_COUNT}, found {len(ISSUES)}."
        )
        sys.exit(1)

    require_gh_auth()
    create_labels()
    create_issues()
    print("\nDone.")


if __name__ == "__main__":
    main()
