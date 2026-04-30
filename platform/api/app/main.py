from __future__ import annotations

import os
import re
import sqlite3
from datetime import UTC, datetime, timedelta

from fastapi import FastAPI, Header, HTTPException, Request

from .control import (
    create_governed_request_record,
    dispatch_approved_governed_request,
    expire_governed_request_if_needed,
    run_governed_request,
    validate_execution_request,
)
from agent_control_stack.executor import ExecutionError
from .models import (
    ApprovalCreateRequest,
    ApprovalRecord,
    ApprovalUpdateRequest,
    GovernedRequestDecisionRequest,
    GovernedRequestRecord,
    AuthConfigResponse,
    AuthSessionResponse,
    DashboardSummaryResponse,
    DemoLoginRequest,
    PolicyProfileRecord,
    PolicyProfileUpdateRequest,
    PolicyProfileVersionRecord,
    ProjectConnectionUpdateRequest,
    ProjectCreateRequest,
    ProjectRecord,
    RunRecord,
    RunRecordDetail,
    RunRequest,
    RunResponse,
    UserRecord,
)
from .store import create_project as persist_project
from .store import create_session_for_user, get_user_by_email, get_user_by_token
from .store import create_approval as persist_approval
from .store import create_policy_profile_version
from .store import current_database_backend
from .store import get_policy_profile as load_policy_profile
from .store import list_policy_profile_versions as load_policy_profile_versions
from .store import get_project_by_id as load_project_by_id
from .store import get_project_by_slug as load_project_by_slug
from .store import get_governed_request as load_governed_request
from .store import get_approval as load_approval
from .store import get_run as load_run
from .store import list_approvals as load_approvals
from .store import list_governed_requests as load_governed_requests
from .store import list_projects as load_projects
from .store import list_runs as load_runs
from .store import next_approval_id
from .store import next_policy_profile_version_id
from .store import project_count
from .store import upsert_user
from .store import update_project as persist_project_update
from .store import upsert_governed_request
from .store import upsert_policy_profile as persist_policy_profile
from .store import update_approval as persist_approval_update


app = FastAPI(
    title="AOS/CDD Platform API",
    version="0.1.0",
    description="Backend for the hosted governed agent-development product.",
)

AUTH_MODE = os.getenv("AOS_CDD_PLATFORM_AUTH_MODE", "demo")
AUTH_PROVIDER_NAME = os.getenv("AOS_CDD_PLATFORM_AUTH_PROVIDER", "Demo Auth")
AUTH_LOGIN_PATH = os.getenv("AOS_CDD_PLATFORM_AUTH_LOGIN_PATH")
EXTERNAL_AUTH_USER_ID_HEADER = os.getenv("AOS_CDD_PLATFORM_AUTH_USER_ID_HEADER", "X-Platform-User-Id")
EXTERNAL_AUTH_USER_EMAIL_HEADER = os.getenv("AOS_CDD_PLATFORM_AUTH_USER_EMAIL_HEADER", "X-Platform-User-Email")
EXTERNAL_AUTH_USER_NAME_HEADER = os.getenv("AOS_CDD_PLATFORM_AUTH_USER_NAME_HEADER", "X-Platform-User-Name")
EXTERNAL_AUTH_USER_ROLE_HEADER = os.getenv("AOS_CDD_PLATFORM_AUTH_USER_ROLE_HEADER", "X-Platform-User-Role")
EXTERNAL_AUTH_DEFAULT_ROLE = os.getenv("AOS_CDD_PLATFORM_AUTH_DEFAULT_ROLE", "member")
PROJECT_LOCK_TIMEOUT = timedelta(hours=1)


@app.get("/health")
def health() -> dict[str, str | int]:
    return {"status": "ok", "projects": project_count(), "database_backend": current_database_backend()}


@app.post("/auth/demo-login", response_model=AuthSessionResponse)
def demo_login(request: DemoLoginRequest) -> AuthSessionResponse:
    if AUTH_MODE != "demo":
        raise HTTPException(status_code=403, detail="demo_auth_disabled")
    user = get_user_by_email(request.email)
    if user is None:
        raise HTTPException(status_code=404, detail="user_not_found")
    token = create_session_for_user(user)
    return AuthSessionResponse(token=token, user=user)


@app.get("/auth/config", response_model=AuthConfigResponse)
def auth_config() -> AuthConfigResponse:
    return AuthConfigResponse(
        mode="external" if AUTH_MODE != "demo" else "demo",
        provider_name=AUTH_PROVIDER_NAME,
        login_path=AUTH_LOGIN_PATH,
    )


@app.get("/auth/me", response_model=UserRecord)
def auth_me(request: Request, authorization: str | None = Header(default=None)) -> UserRecord:
    user = _require_user(request, authorization)
    return user


@app.get("/projects", response_model=list[ProjectRecord])
def list_projects(request: Request, authorization: str | None = Header(default=None)) -> list[ProjectRecord]:
    user = _get_optional_user(request, authorization)
    return load_projects(owner_id=user.user_id if user is not None else None)


@app.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(request: Request, authorization: str | None = Header(default=None)) -> DashboardSummaryResponse:
    user = _require_user(request, authorization)
    projects = load_projects(owner_id=user.user_id)
    runs = load_runs(owner_id=user.user_id)
    approvals = load_approvals(owner_id=user.user_id)

    outcome_counts: dict[str, int] = {}
    for run in runs:
        outcome_counts[run.outcome] = outcome_counts.get(run.outcome, 0) + 1

    policy_profiles_configured = 0
    for project in projects:
        profile = load_policy_profile(project.project_id, user.user_id)
        if profile is not None:
            policy_profiles_configured += 1

    return DashboardSummaryResponse(
        total_projects=len(projects),
        active_projects=sum(1 for project in projects if project.status == "active"),
        connected_projects=sum(1 for project in projects if project.status == "connected"),
        blocked_projects=sum(1 for project in projects if project.status == "blocked"),
        projects_with_repo_connections=sum(1 for project in projects if bool(project.repository_root and project.repository_url)),
        policy_profiles_configured=policy_profiles_configured,
        approvals_total=len(approvals),
        approvals_approved=sum(1 for approval in approvals if approval.status == "approved"),
        runs_total=len(runs),
        policy_critical_paths=sum(1 for approval in approvals if approval.target_class in {"security", "production", "infrastructure"}),
        outcome_counts=outcome_counts,
    )


@app.post("/projects", response_model=ProjectRecord)
def create_project(project: ProjectCreateRequest, request: Request, authorization: str | None = Header(default=None)) -> ProjectRecord:
    user = _require_user(request, authorization)
    slug = _slugify(project.name)
    new_project = ProjectRecord(
        project_id=f"proj_{slug}",
        owner_id=user.user_id,
        owner_name=user.name,
        name=project.name,
        slug=slug,
        repository_url=project.repository_url,
        default_branch=project.default_branch,
        repository_root=project.repository_root,
        status="draft",
        vault_health_status="pending",
        default_context={
            "repository_root": project.repository_root,
            "project_name": project.name,
        }
        if project.repository_root
        else {
            "project_name": project.name,
        },
    )
    try:
        created_project = persist_project(new_project)
        initial_profile = PolicyProfileRecord(
                project_id=created_project.project_id,
                owner_id=user.user_id,
                environment="dev",
                approval_state="unapproved",
                target_class="general",
                destructive_action=False,
                path_privilege=None,
                human_review_required=False,
                notes=["Policy profile created automatically. Tighten this before higher-risk governed execution."],
                updated_at=datetime.now(UTC).isoformat(),
            )
        persist_policy_profile(initial_profile)
        create_policy_profile_version(
            PolicyProfileVersionRecord(
                version_id=next_policy_profile_version_id(),
                project_id=created_project.project_id,
                owner_id=user.user_id,
                previous_state=None,
                new_state=initial_profile.model_dump(),
                changed_by=user.user_id,
                changed_at=initial_profile.updated_at,
                reason="Initial policy profile created during project onboarding.",
            )
        )
        return created_project
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="project_already_exists") from exc


@app.get("/projects/slug/{slug}", response_model=ProjectRecord)
def get_project_by_slug(slug: str, request: Request, authorization: str | None = Header(default=None)) -> ProjectRecord:
    project = load_project_by_slug(slug)
    if project is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    _authorize_project_access(project, request, authorization)
    return project


@app.get("/projects/{project_id}", response_model=ProjectRecord)
def get_project(project_id: str, request: Request, authorization: str | None = Header(default=None)) -> ProjectRecord:
    project = load_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    _authorize_project_access(project, request, authorization)
    return project


@app.post("/projects/{project_id}/connection", response_model=ProjectRecord)
def update_project_connection(
    project_id: str,
    request: ProjectConnectionUpdateRequest,
    http_request: Request,
    authorization: str | None = Header(default=None),
) -> ProjectRecord:
    project = load_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    _authorize_project_access(project, http_request, authorization)
    next_context = dict(project.default_context)
    if request.repository_root:
        next_context["repository_root"] = request.repository_root
    if request.session_loader:
        next_context["session_loader"] = request.session_loader
    if request.policy_artifact:
        next_context["policy_artifact"] = request.policy_artifact
    updated_project = project.model_copy(
        update={
            "repository_url": request.repository_url,
            "default_branch": request.default_branch,
            "repository_root": request.repository_root,
            "session_loader": request.session_loader,
            "policy_artifact": request.policy_artifact,
            "threat_model_document": request.threat_model_document,
            "status": request.status,
            "default_context": next_context,
        }
    )
    try:
        return persist_project_update(updated_project)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="project_connection_update_failed") from exc


@app.get("/projects/{project_id}/policy-profile", response_model=PolicyProfileRecord)
def get_project_policy_profile(project_id: str, request: Request, authorization: str | None = Header(default=None)) -> PolicyProfileRecord:
    project = load_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    user = _require_user(request, authorization)
    _authorize_project_access(project, request, authorization)
    profile = load_policy_profile(project_id, user.user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="policy_profile_not_found")
    return profile


@app.get("/projects/{project_id}/policy-history", response_model=list[PolicyProfileVersionRecord])
def get_project_policy_history(project_id: str, request: Request, authorization: str | None = Header(default=None)) -> list[PolicyProfileVersionRecord]:
    project = load_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    user = _require_user(request, authorization)
    _authorize_project_access(project, request, authorization)
    return load_policy_profile_versions(project_id, user.user_id)


@app.post("/projects/{project_id}/policy-profile", response_model=PolicyProfileRecord)
def upsert_project_policy_profile(
    project_id: str,
    request: PolicyProfileUpdateRequest,
    http_request: Request,
    authorization: str | None = Header(default=None),
) -> PolicyProfileRecord:
    project = load_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    user = _require_user(http_request, authorization)
    _authorize_project_access(project, http_request, authorization)
    previous_profile = load_policy_profile(project_id, user.user_id)
    profile = PolicyProfileRecord(
        project_id=project_id,
        owner_id=user.user_id,
        environment=request.environment,
        approval_state=request.approval_state,
        target_class=request.target_class,
        destructive_action=request.destructive_action,
        path_privilege=request.path_privilege,
        human_review_required=request.human_review_required,
        notes=request.notes,
        updated_at=datetime.now(UTC).isoformat(),
    )
    persisted = persist_policy_profile(profile)
    create_policy_profile_version(
        PolicyProfileVersionRecord(
            version_id=next_policy_profile_version_id(),
            project_id=project_id,
            owner_id=user.user_id,
            previous_state=previous_profile.model_dump() if previous_profile is not None else None,
            new_state=persisted.model_dump(),
            changed_by=user.user_id,
            changed_at=persisted.updated_at,
            reason=request.reason,
        )
    )
    return persisted


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "project"


@app.post("/projects/raw", response_model=ProjectRecord)
def create_raw_project(project: ProjectRecord) -> ProjectRecord:
    try:
        return persist_project(project)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="project_already_exists") from exc


@app.post("/runs/interpret", response_model=RunResponse)
def interpret_run(run_request: RunRequest, request: Request, authorization: str | None = Header(default=None)) -> RunResponse:
    project = get_project(run_request.project_id, request, authorization)
    return run_governed_request(project, run_request.model_copy(update={"execute": False}))


@app.post("/runs/execute", response_model=RunResponse)
def execute_run(run_request: RunRequest, request: Request, authorization: str | None = Header(default=None)) -> RunResponse:
    project = get_project(run_request.project_id, request, authorization)
    try:
        validate_execution_request(project, run_request)
        return run_governed_request(project, run_request.model_copy(update={"execute": True}))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ExecutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/runs", response_model=list[RunRecord])
def list_run_history(
    request: Request,
    project_id: str | None = None,
    authorization: str | None = Header(default=None),
) -> list[RunRecord]:
    user = _require_user(request, authorization)
    if project_id is not None:
        project = load_project_by_id(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="project_not_found")
        _authorize_project_access(project, request, authorization)
    return load_runs(owner_id=user.user_id, project_id=project_id)


@app.get("/requests", response_model=list[GovernedRequestRecord])
def list_governed_request_records(
    request: Request,
    project_id: str | None = None,
    authorization: str | None = Header(default=None),
) -> list[GovernedRequestRecord]:
    user = _require_user(request, authorization)
    if project_id is not None:
        project = load_project_by_id(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="project_not_found")
        _authorize_project_access(project, request, authorization)
    return [expire_governed_request_if_needed(item) for item in load_governed_requests(owner_id=user.user_id, project_id=project_id)]


@app.get("/requests/{request_id}", response_model=GovernedRequestRecord)
def get_governed_request_record(
    request_id: str,
    request: Request,
    authorization: str | None = Header(default=None),
) -> GovernedRequestRecord:
    user = _require_user(request, authorization)
    governed_request = load_governed_request(request_id, user.user_id)
    if governed_request is None:
        raise HTTPException(status_code=404, detail="request_not_found")
    return expire_governed_request_if_needed(governed_request)


@app.post("/requests/submit", response_model=GovernedRequestRecord)
def submit_governed_request(
    run_request: RunRequest,
    request: Request,
    authorization: str | None = Header(default=None),
) -> GovernedRequestRecord:
    project = get_project(run_request.project_id, request, authorization)
    project = _expire_project_lock_if_needed(project)
    if run_request.execute:
        if project.is_processing:
            raise HTTPException(status_code=409, detail="project_request_in_progress")
        project = _set_project_processing(project, True)
    _, governed_request = create_governed_request_record(project, run_request)
    if governed_request.status not in {"PENDING_APPROVAL", "APPROVED", "DISPATCHED", "EXECUTION_FAILED", "FAILED"}:
        project = _set_project_processing(project, False)
    return governed_request


@app.post("/requests/{request_id}/approve", response_model=GovernedRequestRecord)
def approve_governed_request(
    request_id: str,
    decision: GovernedRequestDecisionRequest,
    request: Request,
    authorization: str | None = Header(default=None),
) -> GovernedRequestRecord:
    user = _require_user(request, authorization)
    governed_request = load_governed_request(request_id, user.user_id)
    if governed_request is None:
        raise HTTPException(status_code=404, detail="request_not_found")
    governed_request = expire_governed_request_if_needed(governed_request)
    if governed_request.status != "PENDING_APPROVAL":
        raise HTTPException(status_code=409, detail="request_not_pending_approval")
    approved = governed_request.model_copy(
        update={
            "status": "APPROVED",
            "approval_reason": decision.reason or "Approved in HITL gate",
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )
    upsert_governed_request(approved)
    project = load_project_by_id(approved.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    project = _expire_project_lock_if_needed(project)
    if not project.is_processing:
        project = _set_project_processing(project, True)
    _, dispatched = dispatch_approved_governed_request(project, approved)
    if dispatched.status in {"FAILED", "COMPLETED", "TERMINATED", "PENDING_REVIEW"}:
        _set_project_processing(project, False)
    return dispatched


@app.post("/requests/{request_id}/reject", response_model=GovernedRequestRecord)
def reject_governed_request(
    request_id: str,
    decision: GovernedRequestDecisionRequest,
    request: Request,
    authorization: str | None = Header(default=None),
) -> GovernedRequestRecord:
    user = _require_user(request, authorization)
    governed_request = load_governed_request(request_id, user.user_id)
    if governed_request is None:
        raise HTTPException(status_code=404, detail="request_not_found")
    governed_request = expire_governed_request_if_needed(governed_request)
    rejected = governed_request.model_copy(
        update={
            "status": "REJECTED",
            "rejection_reason": decision.reason or "Rejected in HITL gate",
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )
    upsert_governed_request(rejected)
    updated = rejected.model_copy(
        update={
            "status": "TERMINATED",
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )
    upsert_governed_request(updated)
    project = load_project_by_id(updated.project_id)
    if project is not None:
        _set_project_processing(project, False)
    return updated


@app.post("/requests/{request_id}/escalate", response_model=GovernedRequestRecord)
def escalate_governed_request(
    request_id: str,
    decision: GovernedRequestDecisionRequest,
    request: Request,
    authorization: str | None = Header(default=None),
) -> GovernedRequestRecord:
    user = _require_user(request, authorization)
    governed_request = load_governed_request(request_id, user.user_id)
    if governed_request is None:
        raise HTTPException(status_code=404, detail="request_not_found")
    governed_request = expire_governed_request_if_needed(governed_request)
    escalated = governed_request.model_copy(
        update={
            "status": "ESCALATED",
            "escalation_reason": decision.reason or "Escalated in HITL gate",
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )
    upsert_governed_request(escalated)
    updated = escalated.model_copy(
        update={
            "status": "PENDING_REVIEW",
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )
    upsert_governed_request(updated)
    project = load_project_by_id(updated.project_id)
    if project is not None:
        _set_project_processing(project, False)
    return updated


@app.post("/requests/{request_id}/resubmit", response_model=GovernedRequestRecord)
def resubmit_governed_request(
    request_id: str,
    request: Request,
    authorization: str | None = Header(default=None),
) -> GovernedRequestRecord:
    user = _require_user(request, authorization)
    governed_request = load_governed_request(request_id, user.user_id)
    if governed_request is None:
        raise HTTPException(status_code=404, detail="request_not_found")
    if governed_request.status not in {"FAILED", "TERMINATED", "PENDING_REVIEW"}:
        raise HTTPException(status_code=409, detail="request_not_resubmittable")
    project = load_project_by_id(governed_request.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    project = _expire_project_lock_if_needed(project)
    if project.is_processing:
        raise HTTPException(status_code=409, detail="project_request_in_progress")
    project = _set_project_processing(project, True)
    run_request = RunRequest(
        project_id=governed_request.project_id,
        text=governed_request.request_text,
        execute=True,
        persist=True,
        dry_run=governed_request.dry_run,
        context=governed_request.request_context,
    )
    _, replacement = create_governed_request_record(project, run_request)
    if replacement.status not in {"PENDING_APPROVAL", "APPROVED", "DISPATCHED", "EXECUTION_FAILED", "FAILED"}:
        _set_project_processing(project, False)
    return replacement


@app.post("/projects/{project_id}/force-unlock", response_model=ProjectRecord)
def force_unlock_project(
    project_id: str,
    request: Request,
    authorization: str | None = Header(default=None),
) -> ProjectRecord:
    project = load_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    _authorize_project_access(project, request, authorization)
    return _set_project_processing(project, False)


@app.get("/runs/{run_id}", response_model=RunRecordDetail)
def get_run_detail(run_id: str, request: Request, authorization: str | None = Header(default=None)) -> RunRecordDetail:
    user = _require_user(request, authorization)
    run = load_run(run_id, user.user_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run_not_found")
    return run


@app.get("/approvals", response_model=list[ApprovalRecord])
def list_approval_records(
    request: Request,
    project_id: str | None = None,
    authorization: str | None = Header(default=None),
) -> list[ApprovalRecord]:
    user = _require_user(request, authorization)
    if project_id is not None:
        project = load_project_by_id(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="project_not_found")
        _authorize_project_access(project, request, authorization)
    return load_approvals(owner_id=user.user_id, project_id=project_id)


@app.get("/approvals/{approval_id}", response_model=ApprovalRecord)
def get_approval_record(approval_id: str, request: Request, authorization: str | None = Header(default=None)) -> ApprovalRecord:
    user = _require_user(request, authorization)
    approval = load_approval(approval_id, user.user_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="approval_not_found")
    return approval


@app.post("/approvals", response_model=ApprovalRecord)
def create_approval_record(
    request: ApprovalCreateRequest,
    http_request: Request,
    authorization: str | None = Header(default=None),
) -> ApprovalRecord:
    user = _require_user(http_request, authorization)
    project = load_project_by_id(request.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project_not_found")
    _authorize_project_access(project, http_request, authorization)
    approval = ApprovalRecord(
        approval_id=next_approval_id(),
        project_id=request.project_id,
        owner_id=user.user_id,
        title=request.title,
        status="draft",
        target_class=request.target_class,
        environment=request.environment,
        case_ids=request.case_ids,
        approved_by=[],
        notes=request.notes,
        updated_at=datetime.now(UTC).isoformat(),
    )
    try:
        return persist_approval(approval)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="approval_already_exists") from exc


@app.post("/approvals/{approval_id}", response_model=ApprovalRecord)
def update_approval_record(
    approval_id: str,
    request: ApprovalUpdateRequest,
    http_request: Request,
    authorization: str | None = Header(default=None),
) -> ApprovalRecord:
    user = _require_user(http_request, authorization)
    approval = load_approval(approval_id, user.user_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="approval_not_found")
    updated = approval.model_copy(
        update={
            "status": request.status,
            "approved_by": request.approved_by,
            "notes": request.notes,
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )
    try:
        return persist_approval_update(updated)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="approval_update_failed") from exc


def _extract_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    prefix = "Bearer "
    if authorization.startswith(prefix):
        return authorization[len(prefix):].strip()
    return authorization.strip()


def _get_optional_user(request: Request, authorization: str | None) -> UserRecord | None:
    if AUTH_MODE != "demo":
        return _get_external_user(request)
    token = _extract_token(authorization)
    if not token:
        return None
    return get_user_by_token(token)


def _require_user(request: Request, authorization: str | None) -> UserRecord:
    user = _get_optional_user(request, authorization)
    if user is None:
        raise HTTPException(status_code=401, detail="authentication_required")
    return user


def _authorize_project_access(project: ProjectRecord, request: Request, authorization: str | None) -> None:
    user = _require_user(request, authorization)
    if project.owner_id and project.owner_id != user.user_id and user.role != "admin":
        raise HTTPException(status_code=403, detail="project_access_denied")


def _expire_project_lock_if_needed(project: ProjectRecord) -> ProjectRecord:
    if not project.is_processing or not project.processing_started_at:
        return project
    try:
        started_at = datetime.fromisoformat(project.processing_started_at.replace("Z", "+00:00"))
    except ValueError:
        return _set_project_processing(project, False)
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=UTC)
    if datetime.now(UTC) - started_at < PROJECT_LOCK_TIMEOUT:
        return project
    return _set_project_processing(project, False)


def _set_project_processing(project: ProjectRecord, is_processing: bool) -> ProjectRecord:
    updated = project.model_copy(
        update={
            "is_processing": is_processing,
            "processing_started_at": datetime.now(UTC).isoformat() if is_processing else None,
        }
    )
    return persist_project_update(updated)


def _get_external_user(request: Request) -> UserRecord | None:
    user_id = request.headers.get(EXTERNAL_AUTH_USER_ID_HEADER)
    if not user_id:
        return None
    email = request.headers.get(EXTERNAL_AUTH_USER_EMAIL_HEADER, f"{user_id}@external.local")
    name = request.headers.get(EXTERNAL_AUTH_USER_NAME_HEADER, user_id)
    role_header = request.headers.get(EXTERNAL_AUTH_USER_ROLE_HEADER, EXTERNAL_AUTH_DEFAULT_ROLE)
    role = role_header if role_header in {"owner", "member", "admin"} else EXTERNAL_AUTH_DEFAULT_ROLE
    user = UserRecord(
        user_id=user_id,
        email=email,
        name=name,
        role=role,
    )
    upsert_user(user)
    return user
