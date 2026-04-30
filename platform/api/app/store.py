from __future__ import annotations

import json
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from .models import ApprovalRecord, GovernedRequestRecord, PolicyProfileRecord, PolicyProfileVersionRecord, ProjectRecord, RunRecord, RunRecordDetail, UserRecord

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - optional production dependency
    psycopg = None
    dict_row = None


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_PATH = DATA_DIR / "platform.db"
DATABASE_URL = os.getenv("AOS_CDD_PLATFORM_DATABASE_URL") or os.getenv("DATABASE_URL")
DATABASE_BACKEND = "postgres" if DATABASE_URL and DATABASE_URL.startswith(("postgresql://", "postgres://")) else "sqlite"


SEED_PROJECTS: list[ProjectRecord] = [
    ProjectRecord(
        project_id="proj_agent_control_stack",
        owner_id="user_demo",
        owner_name="A9eel",
        name="Agent Control Stack",
        slug="agent-control-stack",
        repository_url="https://github.com/A9eel-Alharbi/AOS-CDD.git",
        status="active",
        repository_root="D:/Projects/mygithub/v2/aos-cdd-v2",
        session_loader="examples/agent-control-stack/sessions/session-WP-001.yaml",
        policy_artifact="examples/agent-control-stack/ops/policy-profile.yaml",
        approvals_in_force=["APR-001-security-validation"],
        vault_health_status="healthy",
        threat_model_document="examples/agent-control-stack/ops/security-threat-model.md",
        default_context={
            "repository_root": "D:/Projects/mygithub/v2/aos-cdd-v2",
            "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
            "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
        },
        is_processing=False,
        processing_started_at=None,
    ),
    ProjectRecord(
        project_id="proj_gym_revenue_saas",
        owner_id="user_demo",
        owner_name="A9eel",
        name="Gym Revenue SaaS",
        slug="gym-revenue-saas",
        repository_url="https://github.com/acme/gym-saas",
        status="connected",
        repository_root="D:/Projects/mygithub/v2/aos-cdd-v2",
        vault_health_status="pending",
        approvals_in_force=[],
        default_context={
            "repository_root": "D:/Projects/mygithub/v2/aos-cdd-v2",
            "project_name": "Gym Revenue SaaS",
            "project_goal": "Build a governed SaaS API for gym memberships and revenue tracking.",
            "v1_scope": "members, plans, payments, monthly revenue summary",
        },
        is_processing=False,
        processing_started_at=None,
    ),
]

SEED_USERS: list[UserRecord] = [
    UserRecord(
        user_id="user_demo",
        email="demo@aos-cdd.local",
        name="A9eel",
        role="owner",
    )
]

SEED_APPROVALS: list[ApprovalRecord] = [
    ApprovalRecord(
        approval_id="APR-001-security-validation",
        project_id="proj_agent_control_stack",
        owner_id="user_demo",
        title="Production security validation approval",
        status="approved",
        target_class="security",
        environment="prod",
        case_ids=["ops.run_validation"],
        approved_by=["security.lead", "platform.lead"],
        notes=["Allows governed security validation against production-class scope."],
        updated_at="2026-04-29T09:00:00+00:00",
    )
]

SEED_POLICY_PROFILES: list[PolicyProfileRecord] = [
    PolicyProfileRecord(
        project_id="proj_agent_control_stack",
        owner_id="user_demo",
        environment="prod",
        approval_state="approved",
        target_class="security",
        destructive_action=False,
        path_privilege="security-approved",
        human_review_required=True,
        notes=[
            "Governed security validation requires human review before high-risk execution.",
            "Platform mirrors the repo policy profile for request defaults.",
        ],
        updated_at="2026-04-29T09:00:00+00:00",
    ),
    PolicyProfileRecord(
        project_id="proj_gym_revenue_saas",
        owner_id="user_demo",
        environment="dev",
        approval_state="unapproved",
        target_class="general",
        destructive_action=False,
        path_privilege=None,
        human_review_required=False,
        notes=["New project remains in a low-risk draft policy posture until constraints settle."],
        updated_at="2026-04-29T09:05:00+00:00",
    ),
]
SEED_POLICY_PROFILE_VERSIONS: list[PolicyProfileVersionRecord] = [
    PolicyProfileVersionRecord(
        version_id="policy_ver_agent_control_stack_initial",
        project_id="proj_agent_control_stack",
        owner_id="user_demo",
        previous_state=None,
        new_state=SEED_POLICY_PROFILES[0].model_dump(),
        changed_by="user_demo",
        changed_at="2026-04-29T09:00:00+00:00",
        reason="Initial platform policy mirror created from governed repo policy.",
    ),
    PolicyProfileVersionRecord(
        version_id="policy_ver_gym_revenue_saas_initial",
        project_id="proj_gym_revenue_saas",
        owner_id="user_demo",
        previous_state=None,
        new_state=SEED_POLICY_PROFILES[1].model_dump(),
        changed_by="user_demo",
        changed_at="2026-04-29T09:05:00+00:00",
        reason="Initial low-risk draft policy created for new project onboarding.",
    ),
]

SQLITE_AVAILABLE = True
MEMORY_PROJECTS = [project.model_copy(deep=True) for project in SEED_PROJECTS]
MEMORY_USERS = [user.model_copy(deep=True) for user in SEED_USERS]
MEMORY_SESSIONS: dict[str, str] = {}
MEMORY_RUNS: list[RunRecordDetail] = []
MEMORY_APPROVALS = [approval.model_copy(deep=True) for approval in SEED_APPROVALS]
MEMORY_POLICY_PROFILES = [profile.model_copy(deep=True) for profile in SEED_POLICY_PROFILES]
MEMORY_POLICY_PROFILE_VERSIONS = [version.model_copy(deep=True) for version in SEED_POLICY_PROFILE_VERSIONS]
MEMORY_GOVERNED_REQUESTS: list[GovernedRequestRecord] = []
DB_ERRORS: tuple[type[Exception], ...] = (sqlite3.Error,) if DATABASE_BACKEND == "sqlite" else tuple(
    error
    for error in (
        getattr(psycopg, "Error", None),
        getattr(psycopg, "OperationalError", None),
    )
    if error is not None
)


@contextmanager
def _open_connection():
    connection = _connect()
    try:
        yield connection
    finally:
        connection.close()  # type: ignore[attr-defined]


def current_database_backend() -> str:
    return "memory" if not SQLITE_AVAILABLE else DATABASE_BACKEND


def _sql(query: str) -> str:
    if DATABASE_BACKEND != "postgres":
        return query
    return query.replace("?", "%s")


def _execute(connection: object, query: str, params: tuple[object, ...] = ()) -> object:
    if params:
        return connection.execute(_sql(query), params)  # type: ignore[attr-defined]
    return connection.execute(_sql(query))  # type: ignore[attr-defined]


def _ensure_column(connection: object, table: str, column: str, definition: str) -> None:
    if DATABASE_BACKEND == "postgres":
        _execute(connection, f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {definition}")
        return
    rows = _execute(connection, f"PRAGMA table_info({table})").fetchall()
    existing = {row[1] for row in rows}
    if column not in existing:
        _execute(connection, f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_database() -> None:
    global SQLITE_AVAILABLE
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with _open_connection() as connection:
            _execute(
                connection,
                """
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    owner_id TEXT,
                    owner_name TEXT,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL UNIQUE,
                    repository_url TEXT NOT NULL,
                    default_branch TEXT NOT NULL,
                    status TEXT NOT NULL,
                    repository_root TEXT,
                    session_loader TEXT,
                    policy_artifact TEXT,
                    approvals_in_force TEXT NOT NULL,
                    vault_health_status TEXT NOT NULL,
                    threat_model_document TEXT,
                    default_context TEXT NOT NULL,
                    is_processing INTEGER NOT NULL DEFAULT 0,
                    processing_started_at TEXT
                )
                """
            )
            _ensure_column(connection, "projects", "is_processing", "INTEGER NOT NULL DEFAULT 0")
            _ensure_column(connection, "projects", "processing_started_at", "TEXT")
            _execute(
                connection,
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL
                )
                """
            )
            _execute(
                connection,
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL
                )
                """
            )
            _execute(
                connection,
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    owner_id TEXT,
                    created_at TEXT NOT NULL,
                    request_text TEXT NOT NULL,
                    context TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    execution TEXT
                )
                """
            )
            _execute(
                connection,
                """
                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    owner_id TEXT,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    target_class TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    case_ids TEXT NOT NULL,
                    approved_by TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            _execute(
                connection,
                """
                CREATE TABLE IF NOT EXISTS policy_profiles (
                    project_id TEXT PRIMARY KEY,
                    owner_id TEXT,
                    environment TEXT NOT NULL,
                    approval_state TEXT NOT NULL,
                    target_class TEXT NOT NULL,
                    destructive_action INTEGER NOT NULL,
                    path_privilege TEXT,
                    human_review_required INTEGER NOT NULL,
                    notes TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            _execute(
                connection,
                """
                CREATE TABLE IF NOT EXISTS policy_profile_versions (
                    version_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    owner_id TEXT,
                    previous_state TEXT,
                    new_state TEXT NOT NULL,
                    changed_by TEXT NOT NULL,
                    changed_at TEXT NOT NULL,
                    reason TEXT NOT NULL
                )
                """
            )
            _execute(
                connection,
                """
                CREATE TABLE IF NOT EXISTS governed_requests (
                    request_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    owner_id TEXT,
                    request_text TEXT NOT NULL,
                    status TEXT NOT NULL,
                    dry_run INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    outcome TEXT,
                    case_id TEXT,
                    policy_triggers TEXT NOT NULL,
                    intended_actions TEXT NOT NULL,
                    approval_reason TEXT,
                    escalation_reason TEXT,
                    rejection_reason TEXT,
                    failure_summary TEXT,
                    failure_detail TEXT,
                    last_successful_step TEXT,
                    partial_artifacts TEXT NOT NULL,
                    tool_call_log TEXT NOT NULL,
                    request_context TEXT NOT NULL,
                    decision_trace TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT
                )
                """
            )
            existing_count = _execute(connection, "SELECT COUNT(*) FROM projects").fetchone()[0]
            if existing_count == 0:
                for project in SEED_PROJECTS:
                    _insert_project(connection, project)
            user_count = _execute(connection, "SELECT COUNT(*) FROM users").fetchone()[0]
            if user_count == 0:
                for user in SEED_USERS:
                    _execute(
                        connection,
                        "INSERT INTO users (user_id, email, name, role) VALUES (?, ?, ?, ?)",
                        (user.user_id, user.email, user.name, user.role),
                    )
            approval_count = _execute(connection, "SELECT COUNT(*) FROM approvals").fetchone()[0]
            if approval_count == 0:
                for approval in SEED_APPROVALS:
                    _insert_approval(connection, approval)
            policy_profile_count = _execute(connection, "SELECT COUNT(*) FROM policy_profiles").fetchone()[0]
            if policy_profile_count == 0:
                for profile in SEED_POLICY_PROFILES:
                    _insert_policy_profile(connection, profile)
            policy_version_count = _execute(connection, "SELECT COUNT(*) FROM policy_profile_versions").fetchone()[0]
            if policy_version_count == 0:
                for version in SEED_POLICY_PROFILE_VERSIONS:
                    _insert_policy_profile_version(connection, version)
            connection.commit()
    except Exception:
        SQLITE_AVAILABLE = False


def list_projects(owner_id: str | None = None) -> list[ProjectRecord]:
    if not SQLITE_AVAILABLE:
        projects = MEMORY_PROJECTS
        if owner_id is not None:
            projects = [project for project in projects if project.owner_id == owner_id]
        return [project.model_copy(deep=True) for project in projects]
    with _open_connection() as connection:
        if owner_id is not None:
            rows = _execute(
                connection,
                """
                SELECT
                    project_id, owner_id, owner_name, name, slug, repository_url, default_branch, status,
                    repository_root, session_loader, policy_artifact,
                    approvals_in_force, vault_health_status, threat_model_document,
                    default_context, is_processing, processing_started_at
                FROM projects
                WHERE owner_id = ?
                ORDER BY name
                """,
                (owner_id,),
            ).fetchall()
        else:
            rows = _execute(
                connection,
                """
                SELECT
                    project_id, owner_id, owner_name, name, slug, repository_url, default_branch, status,
                    repository_root, session_loader, policy_artifact,
                    approvals_in_force, vault_health_status, threat_model_document,
                    default_context, is_processing, processing_started_at
                FROM projects
                ORDER BY name
                """
            ).fetchall()
    return [_row_to_project(row) for row in rows]


def get_project_by_id(project_id: str) -> ProjectRecord | None:
    if not SQLITE_AVAILABLE:
        for project in MEMORY_PROJECTS:
            if project.project_id == project_id:
                return project.model_copy(deep=True)
        return None
    with _open_connection() as connection:
        row = _execute(
            connection,
            """
            SELECT
                project_id, owner_id, owner_name, name, slug, repository_url, default_branch, status,
                repository_root, session_loader, policy_artifact,
                approvals_in_force, vault_health_status, threat_model_document,
                default_context, is_processing, processing_started_at
            FROM projects
            WHERE project_id = ?
            """,
            (project_id,),
        ).fetchone()
    return _row_to_project(row) if row is not None else None


def get_project_by_slug(slug: str) -> ProjectRecord | None:
    if not SQLITE_AVAILABLE:
        for project in MEMORY_PROJECTS:
            if project.slug == slug:
                return project.model_copy(deep=True)
        return None
    with _open_connection() as connection:
        row = _execute(
            connection,
            """
            SELECT
                project_id, owner_id, owner_name, name, slug, repository_url, default_branch, status,
                repository_root, session_loader, policy_artifact,
                approvals_in_force, vault_health_status, threat_model_document,
                default_context, is_processing, processing_started_at
            FROM projects
            WHERE slug = ?
            """,
            (slug,),
        ).fetchone()
    return _row_to_project(row) if row is not None else None


def create_project(project: ProjectRecord) -> ProjectRecord:
    if not SQLITE_AVAILABLE:
        if any(existing.project_id == project.project_id or existing.slug == project.slug for existing in MEMORY_PROJECTS):
            raise sqlite3.IntegrityError("project already exists")
        MEMORY_PROJECTS.append(project.model_copy(deep=True))
        return project
    try:
        with _open_connection() as connection:
            _insert_project(connection, project)
            connection.commit()
    except Exception as exc:
        _raise_integrity_error(exc)
    return project


def update_project(project: ProjectRecord) -> ProjectRecord:
    if not SQLITE_AVAILABLE:
        for index, existing in enumerate(MEMORY_PROJECTS):
            if existing.project_id == project.project_id and existing.owner_id == project.owner_id:
                MEMORY_PROJECTS[index] = project.model_copy(deep=True)
                return project
        raise sqlite3.IntegrityError("project not found")
    try:
        with _open_connection() as connection:
            _execute(
                connection,
            """
            UPDATE projects
            SET owner_name = ?, name = ?, slug = ?, repository_url = ?, default_branch = ?, status = ?,
                repository_root = ?, session_loader = ?, policy_artifact = ?, approvals_in_force = ?,
                vault_health_status = ?, threat_model_document = ?, default_context = ?,
                is_processing = ?, processing_started_at = ?
            WHERE project_id = ? AND owner_id = ?
            """,
            (
                project.owner_name,
                project.name,
                project.slug,
                project.repository_url,
                project.default_branch,
                project.status,
                project.repository_root,
                project.session_loader,
                project.policy_artifact,
                json.dumps(project.approvals_in_force),
                project.vault_health_status,
                project.threat_model_document,
                json.dumps(project.default_context),
                int(project.is_processing),
                project.processing_started_at,
                project.project_id,
                project.owner_id,
            ),
            )
            connection.commit()
    except Exception as exc:
        _raise_integrity_error(exc)
    return project


def get_policy_profile(project_id: str, owner_id: str) -> PolicyProfileRecord | None:
    if not SQLITE_AVAILABLE:
        for profile in MEMORY_POLICY_PROFILES:
            if profile.project_id == project_id and profile.owner_id == owner_id:
                return profile.model_copy(deep=True)
        return None
    with _open_connection() as connection:
        row = _execute(
            connection,
            """
            SELECT project_id, owner_id, environment, approval_state, target_class,
                   destructive_action, path_privilege, human_review_required, notes, updated_at
            FROM policy_profiles
            WHERE project_id = ? AND owner_id = ?
            """,
            (project_id, owner_id),
        ).fetchone()
    return _row_to_policy_profile(row) if row is not None else None


def upsert_policy_profile(profile: PolicyProfileRecord) -> PolicyProfileRecord:
    if not SQLITE_AVAILABLE:
        for index, existing in enumerate(MEMORY_POLICY_PROFILES):
            if existing.project_id == profile.project_id and existing.owner_id == profile.owner_id:
                MEMORY_POLICY_PROFILES[index] = profile.model_copy(deep=True)
                return profile
        MEMORY_POLICY_PROFILES.append(profile.model_copy(deep=True))
        return profile
    try:
        with _open_connection() as connection:
            _execute(
                connection,
            """
            INSERT INTO policy_profiles (
                project_id, owner_id, environment, approval_state, target_class,
                destructive_action, path_privilege, human_review_required, notes, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
                owner_id = excluded.owner_id,
                environment = excluded.environment,
                approval_state = excluded.approval_state,
                target_class = excluded.target_class,
                destructive_action = excluded.destructive_action,
                path_privilege = excluded.path_privilege,
                human_review_required = excluded.human_review_required,
                notes = excluded.notes,
                updated_at = excluded.updated_at
            """,
            (
                profile.project_id,
                profile.owner_id,
                profile.environment,
                profile.approval_state,
                profile.target_class,
                int(profile.destructive_action),
                profile.path_privilege,
                int(profile.human_review_required),
                json.dumps(profile.notes),
                profile.updated_at,
            ),
            )
            connection.commit()
    except Exception as exc:
        _raise_integrity_error(exc)
    return profile


def list_policy_profile_versions(project_id: str, owner_id: str) -> list[PolicyProfileVersionRecord]:
    if not SQLITE_AVAILABLE:
        versions = [
            version
            for version in MEMORY_POLICY_PROFILE_VERSIONS
            if version.project_id == project_id and version.owner_id == owner_id
        ]
        return [version.model_copy(deep=True) for version in sorted(versions, key=lambda item: item.changed_at, reverse=True)]
    with _open_connection() as connection:
        rows = _execute(
            connection,
            """
            SELECT version_id, project_id, owner_id, previous_state, new_state, changed_by, changed_at, reason
            FROM policy_profile_versions
            WHERE project_id = ? AND owner_id = ?
            ORDER BY changed_at DESC
            """,
            (project_id, owner_id),
        ).fetchall()
    return [_row_to_policy_profile_version(row) for row in rows]


def create_policy_profile_version(version: PolicyProfileVersionRecord) -> PolicyProfileVersionRecord:
    if not SQLITE_AVAILABLE:
        MEMORY_POLICY_PROFILE_VERSIONS.append(version.model_copy(deep=True))
        return version
    try:
        with _open_connection() as connection:
            _insert_policy_profile_version(connection, version)
            connection.commit()
    except Exception as exc:
        _raise_integrity_error(exc)
    return version


def project_count() -> int:
    if not SQLITE_AVAILABLE:
        return len(MEMORY_PROJECTS)
    with _open_connection() as connection:
        return int(_execute(connection, "SELECT COUNT(*) FROM projects").fetchone()[0])


def list_users() -> list[UserRecord]:
    if not SQLITE_AVAILABLE:
        return [user.model_copy(deep=True) for user in MEMORY_USERS]
    with _open_connection() as connection:
        rows = _execute(connection, "SELECT user_id, email, name, role FROM users ORDER BY name").fetchall()
    return [UserRecord(user_id=row["user_id"], email=row["email"], name=row["name"], role=row["role"]) for row in rows]


def upsert_user(user: UserRecord) -> UserRecord:
    if not SQLITE_AVAILABLE:
        for index, existing in enumerate(MEMORY_USERS):
            if existing.user_id == user.user_id or existing.email == user.email:
                MEMORY_USERS[index] = user.model_copy(deep=True)
                return user
        MEMORY_USERS.append(user.model_copy(deep=True))
        return user
    try:
        with _open_connection() as connection:
            _execute(
                connection,
                """
                INSERT INTO users (user_id, email, name, role)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    email = excluded.email,
                    name = excluded.name,
                    role = excluded.role
                """,
                (user.user_id, user.email, user.name, user.role),
            )
            connection.commit()
    except Exception as exc:
        _raise_integrity_error(exc)
    return user


def get_user_by_email(email: str) -> UserRecord | None:
    if not SQLITE_AVAILABLE:
        for user in MEMORY_USERS:
            if user.email == email:
                return user.model_copy(deep=True)
        return None
    with _open_connection() as connection:
        row = _execute(
            connection,
            "SELECT user_id, email, name, role FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    if row is None:
        return None
    return UserRecord(user_id=row["user_id"], email=row["email"], name=row["name"], role=row["role"])


def get_user_by_token(token: str) -> UserRecord | None:
    if not SQLITE_AVAILABLE:
        user_id = MEMORY_SESSIONS.get(token)
        if not user_id:
            return None
        for user in MEMORY_USERS:
            if user.user_id == user_id:
                return user.model_copy(deep=True)
        return None
    with _open_connection() as connection:
        row = _execute(
            connection,
            """
            SELECT u.user_id, u.email, u.name, u.role
            FROM sessions s
            JOIN users u ON u.user_id = s.user_id
            WHERE s.token = ?
            """,
            (token,),
        ).fetchone()
    if row is None:
        return None
    return UserRecord(user_id=row["user_id"], email=row["email"], name=row["name"], role=row["role"])


def create_session_for_user(user: UserRecord) -> str:
    token = secrets.token_urlsafe(24)
    if not SQLITE_AVAILABLE:
        MEMORY_SESSIONS[token] = user.user_id
        return token
    with _open_connection() as connection:
        _execute(
            connection,
            "INSERT INTO sessions (token, user_id) VALUES (?, ?)",
            (token, user.user_id),
        )
        connection.commit()
    return token


def list_runs(owner_id: str, project_id: str | None = None) -> list[RunRecord]:
    if not SQLITE_AVAILABLE:
        runs = [run for run in MEMORY_RUNS if run.owner_id == owner_id]
        if project_id is not None:
            runs = [run for run in runs if run.project_id == project_id]
        return [_detail_to_summary(run) for run in sorted(runs, key=lambda item: item.created_at, reverse=True)]
    with _open_connection() as connection:
        if project_id is not None:
            rows = _execute(
                connection,
                """
                SELECT run_id, project_id, owner_id, created_at, request_text, decision, execution
                FROM runs
                WHERE owner_id = ? AND project_id = ?
                ORDER BY created_at DESC
                """,
                (owner_id, project_id),
            ).fetchall()
        else:
            rows = _execute(
                connection,
                """
                SELECT run_id, project_id, owner_id, created_at, request_text, decision, execution
                FROM runs
                WHERE owner_id = ?
                ORDER BY created_at DESC
                """,
                (owner_id,),
            ).fetchall()
    return [_row_to_run_summary(row) for row in rows]


def get_run(run_id: str, owner_id: str) -> RunRecordDetail | None:
    if not SQLITE_AVAILABLE:
        for run in MEMORY_RUNS:
            if run.run_id == run_id and run.owner_id == owner_id:
                return run.model_copy(deep=True)
        return None
    with _open_connection() as connection:
        row = _execute(
            connection,
            """
            SELECT run_id, project_id, owner_id, created_at, request_text, context, decision, execution
            FROM runs
            WHERE run_id = ? AND owner_id = ?
            """,
            (run_id, owner_id),
        ).fetchone()
    return _row_to_run_detail(row) if row is not None else None


def list_governed_requests(owner_id: str, project_id: str | None = None) -> list[GovernedRequestRecord]:
    if not SQLITE_AVAILABLE:
        requests = [request for request in MEMORY_GOVERNED_REQUESTS if request.owner_id == owner_id]
        if project_id is not None:
            requests = [request for request in requests if request.project_id == project_id]
        return [request.model_copy(deep=True) for request in sorted(requests, key=lambda item: item.updated_at, reverse=True)]
    with _open_connection() as connection:
        if project_id is not None:
            rows = _execute(
                connection,
                """
                SELECT * FROM governed_requests
                WHERE owner_id = ? AND project_id = ?
                ORDER BY updated_at DESC
                """,
                (owner_id, project_id),
            ).fetchall()
        else:
            rows = _execute(
                connection,
                """
                SELECT * FROM governed_requests
                WHERE owner_id = ?
                ORDER BY updated_at DESC
                """,
                (owner_id,),
            ).fetchall()
    return [_row_to_governed_request(row) for row in rows]


def get_governed_request(request_id: str, owner_id: str) -> GovernedRequestRecord | None:
    if not SQLITE_AVAILABLE:
        for request in MEMORY_GOVERNED_REQUESTS:
            if request.request_id == request_id and request.owner_id == owner_id:
                return request.model_copy(deep=True)
        return None
    with _open_connection() as connection:
        row = _execute(
            connection,
            """
            SELECT * FROM governed_requests
            WHERE request_id = ? AND owner_id = ?
            """,
            (request_id, owner_id),
        ).fetchone()
    return _row_to_governed_request(row) if row is not None else None


def upsert_governed_request(record: GovernedRequestRecord) -> GovernedRequestRecord:
    if not SQLITE_AVAILABLE:
        for index, existing in enumerate(MEMORY_GOVERNED_REQUESTS):
            if existing.request_id == record.request_id and existing.owner_id == record.owner_id:
                MEMORY_GOVERNED_REQUESTS[index] = record.model_copy(deep=True)
                return record
        MEMORY_GOVERNED_REQUESTS.append(record.model_copy(deep=True))
        return record
    try:
        with _open_connection() as connection:
            _execute(
                connection,
                """
                INSERT INTO governed_requests (
                    request_id, project_id, owner_id, request_text, status, dry_run, risk_level,
                    outcome, case_id, policy_triggers, intended_actions, approval_reason,
                    escalation_reason, rejection_reason, failure_summary, failure_detail,
                    last_successful_step, partial_artifacts, tool_call_log, request_context,
                    decision_trace, created_at, updated_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(request_id) DO UPDATE SET
                    project_id = excluded.project_id,
                    owner_id = excluded.owner_id,
                    request_text = excluded.request_text,
                    status = excluded.status,
                    dry_run = excluded.dry_run,
                    risk_level = excluded.risk_level,
                    outcome = excluded.outcome,
                    case_id = excluded.case_id,
                    policy_triggers = excluded.policy_triggers,
                    intended_actions = excluded.intended_actions,
                    approval_reason = excluded.approval_reason,
                    escalation_reason = excluded.escalation_reason,
                    rejection_reason = excluded.rejection_reason,
                    failure_summary = excluded.failure_summary,
                    failure_detail = excluded.failure_detail,
                    last_successful_step = excluded.last_successful_step,
                    partial_artifacts = excluded.partial_artifacts,
                    tool_call_log = excluded.tool_call_log,
                    request_context = excluded.request_context,
                    decision_trace = excluded.decision_trace,
                    updated_at = excluded.updated_at,
                    expires_at = excluded.expires_at
                """,
                _governed_request_params(record),
            )
            connection.commit()
    except Exception as exc:
        _raise_integrity_error(exc)
    return record


def create_run_record(detail: RunRecordDetail) -> RunRecordDetail:
    if not SQLITE_AVAILABLE:
        MEMORY_RUNS.append(detail.model_copy(deep=True))
        return detail
    with _open_connection() as connection:
        _execute(
            connection,
            """
            INSERT INTO runs (run_id, project_id, owner_id, created_at, request_text, context, decision, execution)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                detail.run_id,
                detail.project_id,
                detail.owner_id,
                detail.created_at,
                detail.request_text,
                json.dumps(detail.context),
                json.dumps(detail.decision.model_dump()),
                json.dumps(detail.execution.model_dump()) if detail.execution is not None else None,
            ),
        )
        connection.commit()
    return detail


def next_run_id() -> str:
    return f"run_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"


def next_governed_request_id() -> str:
    return f"req_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{secrets.token_hex(4)}"


def next_approval_id() -> str:
    return f"APR-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(2).upper()}"


def next_policy_profile_version_id() -> str:
    return f"POLVER-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(2).upper()}"


def list_approvals(owner_id: str, project_id: str | None = None) -> list[ApprovalRecord]:
    if not SQLITE_AVAILABLE:
        approvals = [approval for approval in MEMORY_APPROVALS if approval.owner_id == owner_id]
        if project_id is not None:
            approvals = [approval for approval in approvals if approval.project_id == project_id]
        return [approval.model_copy(deep=True) for approval in sorted(approvals, key=lambda item: item.updated_at, reverse=True)]
    with _open_connection() as connection:
        if project_id is not None:
            rows = _execute(
                connection,
                """
                SELECT approval_id, project_id, owner_id, title, status, target_class, environment,
                       case_ids, approved_by, notes, updated_at
                FROM approvals
                WHERE owner_id = ? AND project_id = ?
                ORDER BY updated_at DESC
                """,
                (owner_id, project_id),
            ).fetchall()
        else:
            rows = _execute(
                connection,
                """
                SELECT approval_id, project_id, owner_id, title, status, target_class, environment,
                       case_ids, approved_by, notes, updated_at
                FROM approvals
                WHERE owner_id = ?
                ORDER BY updated_at DESC
                """,
                (owner_id,),
            ).fetchall()
    return [_row_to_approval(row) for row in rows]


def get_approval(approval_id: str, owner_id: str) -> ApprovalRecord | None:
    if not SQLITE_AVAILABLE:
        for approval in MEMORY_APPROVALS:
            if approval.approval_id == approval_id and approval.owner_id == owner_id:
                return approval.model_copy(deep=True)
        return None
    with _open_connection() as connection:
        row = _execute(
            connection,
            """
            SELECT approval_id, project_id, owner_id, title, status, target_class, environment,
                   case_ids, approved_by, notes, updated_at
            FROM approvals
            WHERE approval_id = ? AND owner_id = ?
            """,
            (approval_id, owner_id),
        ).fetchone()
    return _row_to_approval(row) if row is not None else None


def create_approval(approval: ApprovalRecord) -> ApprovalRecord:
    if not SQLITE_AVAILABLE:
        if any(existing.approval_id == approval.approval_id for existing in MEMORY_APPROVALS):
            raise sqlite3.IntegrityError("approval already exists")
        MEMORY_APPROVALS.append(approval.model_copy(deep=True))
        return approval
    try:
        with _open_connection() as connection:
            _insert_approval(connection, approval)
            connection.commit()
    except Exception as exc:
        _raise_integrity_error(exc)
    return approval


def update_approval(approval: ApprovalRecord) -> ApprovalRecord:
    if not SQLITE_AVAILABLE:
        for index, existing in enumerate(MEMORY_APPROVALS):
            if existing.approval_id == approval.approval_id and existing.owner_id == approval.owner_id:
                MEMORY_APPROVALS[index] = approval.model_copy(deep=True)
                return approval
        raise sqlite3.IntegrityError("approval not found")
    try:
        with _open_connection() as connection:
            _execute(
                connection,
            """
            UPDATE approvals
            SET status = ?, approved_by = ?, notes = ?, updated_at = ?
            WHERE approval_id = ? AND owner_id = ?
            """,
            (
                approval.status,
                json.dumps(approval.approved_by),
                json.dumps(approval.notes),
                approval.updated_at,
                approval.approval_id,
                approval.owner_id,
            ),
            )
            connection.commit()
    except Exception as exc:
        _raise_integrity_error(exc)
    return approval


def _insert_project(connection: sqlite3.Connection, project: ProjectRecord) -> None:
    payload = project.model_dump()
    _execute(
        connection,
        """
        INSERT INTO projects (
            project_id, owner_id, owner_name, name, slug, repository_url, default_branch, status,
            repository_root, session_loader, policy_artifact,
            approvals_in_force, vault_health_status, threat_model_document,
            default_context, is_processing, processing_started_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["project_id"],
            payload.get("owner_id"),
            payload.get("owner_name"),
            payload["name"],
            payload["slug"],
            payload["repository_url"],
            payload["default_branch"],
            payload["status"],
            payload.get("repository_root"),
            payload.get("session_loader"),
            payload.get("policy_artifact"),
            json.dumps(payload.get("approvals_in_force", [])),
            payload.get("vault_health_status", "pending"),
            payload.get("threat_model_document"),
            json.dumps(payload.get("default_context", {})),
            int(payload.get("is_processing", False)),
            payload.get("processing_started_at"),
        ),
    )


def _insert_approval(connection: sqlite3.Connection, approval: ApprovalRecord) -> None:
    payload = approval.model_dump()
    _execute(
        connection,
        """
        INSERT INTO approvals (
            approval_id, project_id, owner_id, title, status, target_class, environment,
            case_ids, approved_by, notes, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["approval_id"],
            payload["project_id"],
            payload.get("owner_id"),
            payload["title"],
            payload["status"],
            payload["target_class"],
            payload["environment"],
            json.dumps(payload.get("case_ids", [])),
            json.dumps(payload.get("approved_by", [])),
            json.dumps(payload.get("notes", [])),
            payload["updated_at"],
        ),
    )


def _insert_policy_profile(connection: sqlite3.Connection, profile: PolicyProfileRecord) -> None:
    payload = profile.model_dump()
    _execute(
        connection,
        """
        INSERT INTO policy_profiles (
            project_id, owner_id, environment, approval_state, target_class,
            destructive_action, path_privilege, human_review_required, notes, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["project_id"],
            payload.get("owner_id"),
            payload["environment"],
            payload["approval_state"],
            payload["target_class"],
            int(payload["destructive_action"]),
            payload.get("path_privilege"),
            int(payload["human_review_required"]),
            json.dumps(payload.get("notes", [])),
            payload["updated_at"],
        ),
    )


def _insert_policy_profile_version(connection: sqlite3.Connection, version: PolicyProfileVersionRecord) -> None:
    payload = version.model_dump()
    _execute(
        connection,
        """
        INSERT INTO policy_profile_versions (
            version_id, project_id, owner_id, previous_state, new_state, changed_by, changed_at, reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["version_id"],
            payload["project_id"],
            payload.get("owner_id"),
            json.dumps(payload.get("previous_state")) if payload.get("previous_state") is not None else None,
            json.dumps(payload["new_state"]),
            payload["changed_by"],
            payload["changed_at"],
            payload["reason"],
        ),
    )


def _row_to_project(row: sqlite3.Row) -> ProjectRecord:
    return ProjectRecord(
        project_id=row["project_id"],
        owner_id=row["owner_id"],
        owner_name=row["owner_name"],
        name=row["name"],
        slug=row["slug"],
        repository_url=row["repository_url"],
        default_branch=row["default_branch"],
        status=row["status"],
        repository_root=row["repository_root"],
        session_loader=row["session_loader"],
        policy_artifact=row["policy_artifact"],
        approvals_in_force=json.loads(row["approvals_in_force"]),
        vault_health_status=row["vault_health_status"],
        threat_model_document=row["threat_model_document"],
        default_context=json.loads(row["default_context"]),
        is_processing=bool(row["is_processing"]),
        processing_started_at=row["processing_started_at"],
    )


def _detail_to_summary(detail: RunRecordDetail) -> RunRecord:
    return RunRecord(
        run_id=detail.run_id,
        project_id=detail.project_id,
        owner_id=detail.owner_id,
        text=detail.request_text,
        outcome=detail.decision.outcome,
        case_id=detail.decision.case_id,
        execution_status=detail.execution.status if detail.execution is not None else None,
        created_at=detail.created_at,
        rationale=detail.decision.rationale,
    )


def _row_to_run_summary(row: sqlite3.Row) -> RunRecord:
    decision = json.loads(row["decision"])
    execution = json.loads(row["execution"]) if row["execution"] else None
    return RunRecord(
        run_id=row["run_id"],
        project_id=row["project_id"],
        owner_id=row["owner_id"],
        text=row["request_text"],
        outcome=decision["outcome"],
        case_id=decision.get("case_id"),
        execution_status=execution.get("status") if execution else None,
        created_at=row["created_at"],
        rationale=decision["rationale"],
    )


def _row_to_run_detail(row: sqlite3.Row) -> RunRecordDetail:
    return RunRecordDetail(
        run_id=row["run_id"],
        project_id=row["project_id"],
        owner_id=row["owner_id"],
        created_at=row["created_at"],
        request_text=row["request_text"],
        context=json.loads(row["context"]),
        decision=json.loads(row["decision"]),
        execution=json.loads(row["execution"]) if row["execution"] else None,
    )


def _row_to_approval(row: sqlite3.Row) -> ApprovalRecord:
    return ApprovalRecord(
        approval_id=row["approval_id"],
        project_id=row["project_id"],
        owner_id=row["owner_id"],
        title=row["title"],
        status=row["status"],
        target_class=row["target_class"],
        environment=row["environment"],
        case_ids=json.loads(row["case_ids"]),
        approved_by=json.loads(row["approved_by"]),
        notes=json.loads(row["notes"]),
        updated_at=row["updated_at"],
    )


def _row_to_policy_profile(row: sqlite3.Row) -> PolicyProfileRecord:
    return PolicyProfileRecord(
        project_id=row["project_id"],
        owner_id=row["owner_id"],
        environment=row["environment"],
        approval_state=row["approval_state"],
        target_class=row["target_class"],
        destructive_action=bool(row["destructive_action"]),
        path_privilege=row["path_privilege"],
        human_review_required=bool(row["human_review_required"]),
        notes=json.loads(row["notes"]),
        updated_at=row["updated_at"],
    )


def _row_to_policy_profile_version(row: sqlite3.Row) -> PolicyProfileVersionRecord:
    return PolicyProfileVersionRecord(
        version_id=row["version_id"],
        project_id=row["project_id"],
        owner_id=row["owner_id"],
        previous_state=json.loads(row["previous_state"]) if row["previous_state"] else None,
        new_state=json.loads(row["new_state"]),
        changed_by=row["changed_by"],
        changed_at=row["changed_at"],
        reason=row["reason"],
    )


def _row_to_governed_request(row: sqlite3.Row) -> GovernedRequestRecord:
    return GovernedRequestRecord(
        request_id=row["request_id"],
        project_id=row["project_id"],
        owner_id=row["owner_id"],
        request_text=row["request_text"],
        status=row["status"],
        dry_run=bool(row["dry_run"]),
        risk_level=row["risk_level"],
        outcome=row["outcome"],
        case_id=row["case_id"],
        policy_triggers=json.loads(row["policy_triggers"]),
        intended_actions=json.loads(row["intended_actions"]),
        approval_reason=row["approval_reason"],
        escalation_reason=row["escalation_reason"],
        rejection_reason=row["rejection_reason"],
        failure_summary=row["failure_summary"],
        failure_detail=row["failure_detail"],
        last_successful_step=row["last_successful_step"],
        partial_artifacts=json.loads(row["partial_artifacts"]),
        tool_call_log=json.loads(row["tool_call_log"]),
        request_context=json.loads(row["request_context"]),
        decision_trace=json.loads(row["decision_trace"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        expires_at=row["expires_at"],
    )


def _governed_request_params(record: GovernedRequestRecord) -> tuple[object, ...]:
    return (
        record.request_id,
        record.project_id,
        record.owner_id,
        record.request_text,
        record.status,
        int(record.dry_run),
        record.risk_level,
        record.outcome,
        record.case_id,
        json.dumps(record.policy_triggers),
        json.dumps(record.intended_actions),
        record.approval_reason,
        record.escalation_reason,
        record.rejection_reason,
        record.failure_summary,
        record.failure_detail,
        record.last_successful_step,
        json.dumps(record.partial_artifacts),
        json.dumps(record.tool_call_log),
        json.dumps(record.request_context),
        json.dumps(record.decision_trace),
        record.created_at,
        record.updated_at,
        record.expires_at,
    )


def _raise_integrity_error(exc: Exception) -> None:
    if isinstance(exc, sqlite3.IntegrityError):
        raise exc
    postgres_integrity_error = getattr(psycopg, "IntegrityError", None)
    if postgres_integrity_error is not None and isinstance(exc, postgres_integrity_error):
        raise sqlite3.IntegrityError(str(exc)) from exc
    raise exc


def _connect() -> object:
    if DATABASE_BACKEND == "postgres":
        if psycopg is None or dict_row is None:
            raise RuntimeError("psycopg is required for PostgreSQL backend support")
        return psycopg.connect(DATABASE_URL, row_factory=dict_row)
    connection = sqlite3.connect(DB_PATH, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


init_database()
