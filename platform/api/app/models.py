from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ProjectRecord(BaseModel):
    project_id: str = Field(..., examples=["proj_demo"])
    owner_id: str | None = None
    owner_name: str | None = None
    name: str
    slug: str
    repository_url: str
    default_branch: str = "main"
    status: Literal["draft", "connected", "active", "blocked"] = "draft"
    repository_root: str | None = None
    session_loader: str | None = None
    policy_artifact: str | None = None
    approvals_in_force: list[str] = Field(default_factory=list)
    vault_health_status: Literal["healthy", "review", "degraded", "pending"] = "pending"
    threat_model_document: str | None = None
    default_context: dict[str, Any] = Field(default_factory=dict)
    is_processing: bool = False
    processing_started_at: str | None = None


class ProjectCreateRequest(BaseModel):
    name: str
    repository_url: str
    default_branch: str = "main"
    repository_root: str | None = None


class ProjectConnectionUpdateRequest(BaseModel):
    repository_url: str
    default_branch: str = "main"
    repository_root: str | None = None
    session_loader: str | None = None
    policy_artifact: str | None = None
    threat_model_document: str | None = None
    status: Literal["draft", "connected", "active", "blocked"] = "connected"


class UserRecord(BaseModel):
    user_id: str
    email: str
    name: str
    role: Literal["owner", "member", "admin"] = "owner"


class DemoLoginRequest(BaseModel):
    email: str


class AuthSessionResponse(BaseModel):
    token: str
    user: UserRecord


class AuthConfigResponse(BaseModel):
    mode: Literal["demo", "external"]
    provider_name: str
    login_path: str | None = None


class RunRequest(BaseModel):
    project_id: str
    text: str
    execute: bool = False
    persist: bool = False
    dry_run: bool = False
    context: dict[str, Any] = Field(default_factory=dict)


class RunEnvelope(BaseModel):
    raw_input: str
    restored_input: str
    normalized_input: str
    outcome: Literal["clarify", "refuse", "dispatch", "escalate"]
    rationale: str
    case_id: str | None = None
    clarification_question: str | None = None
    refusal_reason: str | None = None
    escalation_reason: str | None = None
    dispatch_target: dict[str, Any] | None = None
    decision_trace: list[dict[str, Any]] = Field(default_factory=list)


class RunExecution(BaseModel):
    status: str
    procedure: str
    target: str
    details: dict[str, Any] = Field(default_factory=dict)


class RunResponse(BaseModel):
    project: ProjectRecord
    context: dict[str, Any]
    decision: RunEnvelope
    execution: RunExecution | None = None


class RunRecord(BaseModel):
    run_id: str
    project_id: str
    owner_id: str | None = None
    text: str
    outcome: Literal["clarify", "refuse", "dispatch", "escalate"]
    case_id: str | None = None
    execution_status: str | None = None
    created_at: str
    rationale: str


class RunRecordDetail(BaseModel):
    run_id: str
    project_id: str
    owner_id: str | None = None
    created_at: str
    request_text: str
    context: dict[str, Any]
    decision: RunEnvelope
    execution: RunExecution | None = None


class ApprovalRecord(BaseModel):
    approval_id: str
    project_id: str
    owner_id: str | None = None
    title: str
    status: Literal["draft", "approved", "rejected", "expired"] = "draft"
    target_class: Literal["general", "security", "production", "infrastructure"] = "general"
    environment: Literal["dev", "staging", "prod"] = "dev"
    case_ids: list[str] = Field(default_factory=list)
    approved_by: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    updated_at: str


class ApprovalCreateRequest(BaseModel):
    project_id: str
    title: str
    target_class: Literal["general", "security", "production", "infrastructure"] = "general"
    environment: Literal["dev", "staging", "prod"] = "dev"
    case_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ApprovalUpdateRequest(BaseModel):
    status: Literal["draft", "approved", "rejected", "expired"]
    approved_by: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class PolicyProfileRecord(BaseModel):
    project_id: str
    owner_id: str | None = None
    environment: Literal["dev", "staging", "prod"] = "dev"
    approval_state: Literal["unapproved", "approved"] = "unapproved"
    target_class: Literal["general", "security", "production", "infrastructure"] = "general"
    destructive_action: bool = False
    path_privilege: str | None = None
    human_review_required: bool = False
    notes: list[str] = Field(default_factory=list)
    updated_at: str


class PolicyProfileUpdateRequest(BaseModel):
    environment: Literal["dev", "staging", "prod"] = "dev"
    approval_state: Literal["unapproved", "approved"] = "unapproved"
    target_class: Literal["general", "security", "production", "infrastructure"] = "general"
    destructive_action: bool = False
    path_privilege: str | None = None
    human_review_required: bool = False
    notes: list[str] = Field(default_factory=list)
    reason: str = Field(..., min_length=1)


class PolicyProfileVersionRecord(BaseModel):
    version_id: str
    project_id: str
    owner_id: str | None = None
    previous_state: dict[str, Any] | None = None
    new_state: dict[str, Any]
    changed_by: str
    changed_at: str
    reason: str


class DashboardSummaryResponse(BaseModel):
    total_projects: int
    active_projects: int
    connected_projects: int
    blocked_projects: int
    projects_with_repo_connections: int
    policy_profiles_configured: int
    approvals_total: int
    approvals_approved: int
    runs_total: int
    policy_critical_paths: int
    outcome_counts: dict[str, int] = Field(default_factory=dict)


class GovernedRequestRecord(BaseModel):
    request_id: str
    project_id: str
    owner_id: str | None = None
    request_text: str
    status: Literal[
        "SUBMITTED",
        "CLASSIFIED",
        "PENDING_APPROVAL",
        "APPROVED",
        "DISPATCHED",
        "REJECTED",
        "TERMINATED",
        "ESCALATED",
        "PENDING_REVIEW",
        "EXECUTION_FAILED",
        "FAILED",
        "COMPLETED",
    ]
    dry_run: bool = False
    risk_level: Literal["low", "medium", "high"] = "low"
    outcome: Literal["clarify", "refuse", "dispatch", "escalate"] | None = None
    case_id: str | None = None
    policy_triggers: list[str] = Field(default_factory=list)
    intended_actions: list[str] = Field(default_factory=list)
    approval_reason: str | None = None
    escalation_reason: str | None = None
    rejection_reason: str | None = None
    failure_summary: str | None = None
    failure_detail: str | None = None
    last_successful_step: str | None = None
    partial_artifacts: list[str] = Field(default_factory=list)
    tool_call_log: list[dict[str, Any]] = Field(default_factory=list)
    request_context: dict[str, Any] = Field(default_factory=dict)
    decision_trace: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str
    updated_at: str
    expires_at: str | None = None


class GovernedRequestDecisionRequest(BaseModel):
    reason: str = ""
