from __future__ import annotations

import sys
import traceback
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .models import GovernedRequestRecord, PolicyProfileRecord, ProjectRecord, RunRecordDetail, RunRequest, RunResponse
from .store import create_run_record, get_governed_request, get_policy_profile, next_governed_request_id, next_run_id, upsert_governed_request


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_control_stack.executor import ExecutionFailure, GovernedExecutor
from agent_control_stack.pipeline import AgentControlPipeline

REGISTRY_PATH = ROOT / "agent_control_stack" / "runtime" / "case_registry.yaml"
PENDING_APPROVAL_TTL = timedelta(hours=4)


def run_governed_request(project: ProjectRecord, request: RunRequest) -> RunResponse:
    pipeline = AgentControlPipeline.from_registry_file(REGISTRY_PATH)
    executor = GovernedExecutor()

    policy_profile = get_policy_profile(project.project_id, project.owner_id or "")
    resolved_context = _build_resolved_context(project, request.context, policy_profile, request.dry_run)

    decision = pipeline.decide(request.text, resolved_context)
    execution = None
    if request.execute and decision.outcome == "dispatch":
        execution = executor.execute(decision, resolved_context)
        execution_payload = execution.to_dict()
        execution_payload["details"] = execution_payload.pop("payload", {})
        execution = execution_payload

    response = RunResponse(
        project=project,
        context=resolved_context,
        decision=decision.to_dict(),
        execution=execution,
    )
    if request.persist:
        create_run_record(
            RunRecordDetail(
                run_id=next_run_id(),
                project_id=project.project_id,
                owner_id=project.owner_id,
                created_at=datetime.now(UTC).isoformat(),
                request_text=request.text,
                context=resolved_context,
                decision=response.decision,
                execution=response.execution,
            )
        )
    return response


def create_governed_request_record(project: ProjectRecord, request: RunRequest) -> tuple[RunResponse, GovernedRequestRecord]:
    response = run_governed_request(project, request.model_copy(update={"persist": False, "execute": False}))
    decision = response.decision.model_dump() if hasattr(response.decision, "model_dump") else response.decision
    now = datetime.now(UTC).isoformat()
    status = _status_for_response(decision["outcome"], request.execute)
    record = GovernedRequestRecord(
        request_id=next_governed_request_id(),
        project_id=project.project_id,
        owner_id=project.owner_id,
        request_text=request.text,
        status=status,
        dry_run=request.dry_run,
        risk_level=_risk_level(response),
        outcome=decision["outcome"],
        case_id=decision.get("case_id"),
        policy_triggers=_policy_triggers(response),
        intended_actions=_intended_actions(response),
        escalation_reason=decision.get("escalation_reason"),
        rejection_reason=decision.get("refusal_reason"),
        request_context=response.context,
        decision_trace=decision.get("decision_trace", []),
        created_at=now,
        updated_at=now,
        expires_at=_expiry_for_status(status),
    )
    upsert_governed_request(record)
    return response, record


def dispatch_approved_governed_request(project: ProjectRecord, request_record: GovernedRequestRecord) -> tuple[RunResponse | None, GovernedRequestRecord]:
    request = RunRequest(
        project_id=request_record.project_id,
        text=request_record.request_text,
        execute=True,
        persist=True,
        dry_run=request_record.dry_run,
        context=request_record.request_context,
    )
    try:
        response = run_governed_request(project, request)
        updated = request_record.model_copy(
            update={
                "status": "COMPLETED" if response.execution is not None else "DISPATCHED",
                "updated_at": datetime.now(UTC).isoformat(),
                "partial_artifacts": _partial_artifacts_from_execution(response),
                "tool_call_log": _tool_log_from_execution(response),
                "last_successful_step": "execution_completed" if response.execution is not None else "classified_only",
                "failure_summary": None,
                "failure_detail": None,
            }
        )
    except ExecutionFailure as exc:
        updated = request_record.model_copy(
            update={
                "status": "EXECUTION_FAILED",
                "updated_at": datetime.now(UTC).isoformat(),
                "failure_summary": f"Execution failed: {type(exc).__name__}",
                "failure_detail": traceback.format_exc(),
                "last_successful_step": exc.last_successful_step or "dispatch_started",
                "partial_artifacts": exc.partial_artifacts,
                "tool_call_log": exc.tool_call_log,
            }
        )
        upsert_governed_request(updated)
        failed = updated.model_copy(
            update={
                "status": "FAILED",
                "updated_at": datetime.now(UTC).isoformat(),
                "last_successful_step": "execution_failed",
            }
        )
        upsert_governed_request(failed)
        return None, failed
    except Exception as exc:
        updated = request_record.model_copy(
            update={
                "status": "EXECUTION_FAILED",
                "updated_at": datetime.now(UTC).isoformat(),
                "failure_summary": f"Execution failed: {type(exc).__name__}",
                "failure_detail": traceback.format_exc(),
                "last_successful_step": "dispatch_started",
                "tool_call_log": [{"step": "execution_error", "detail": str(exc), "status": "failed"}],
            }
        )
        upsert_governed_request(updated)
        failed = updated.model_copy(
            update={
                "status": "FAILED",
                "updated_at": datetime.now(UTC).isoformat(),
                "last_successful_step": "execution_failed",
            }
        )
        upsert_governed_request(failed)
        return None, failed
    upsert_governed_request(updated)
    return response, updated


def validate_execution_request(project: ProjectRecord, request: RunRequest) -> None:
    policy_profile = get_policy_profile(project.project_id, project.owner_id or "")
    merged_context = _build_resolved_context(project, request.context, policy_profile, request.dry_run)
    if request.execute and not merged_context.get("repository_root"):
        # repo-root execution is a hard requirement for governed runtime flows
        raise ValueError("repository_root is required when execute=true")


def _build_resolved_context(
    project: ProjectRecord,
    request_context: dict[str, object],
    policy_profile: PolicyProfileRecord | None,
    dry_run: bool = False,
) -> dict[str, object]:
    resolved_context: dict[str, object] = dict(project.default_context)
    if policy_profile is not None:
        existing_policy = resolved_context.get("policy")
        merged_policy = dict(existing_policy) if isinstance(existing_policy, dict) else {}
        merged_policy.update(
            {
                "environment": policy_profile.environment,
                "approval_state": policy_profile.approval_state,
                "target_class": policy_profile.target_class,
                "destructive_action": policy_profile.destructive_action,
                "human_review_required": policy_profile.human_review_required,
            }
        )
        if policy_profile.path_privilege:
            merged_policy["path_privilege"] = policy_profile.path_privilege
        resolved_context["policy"] = merged_policy
    if dry_run or request_context.get("mode") == "DRY_RUN":
        resolved_context["mode"] = "DRY_RUN"

    for key, value in request_context.items():
        if key == "policy" and isinstance(value, dict):
            existing_policy = resolved_context.get("policy")
            merged_policy = dict(existing_policy) if isinstance(existing_policy, dict) else {}
            merged_policy.update(value)
            resolved_context["policy"] = merged_policy
            continue
        resolved_context[key] = value
    return resolved_context


def _status_for_response(outcome: str, execute: bool) -> str:
    if outcome == "dispatch":
        return "PENDING_APPROVAL" if execute else "CLASSIFIED"
    if outcome == "clarify":
        return "TERMINATED"
    if outcome == "refuse":
        return "TERMINATED"
    if outcome == "escalate":
        return "PENDING_REVIEW"
    return "CLASSIFIED"


def _risk_level(response: RunResponse) -> str:
    policy = response.context.get("policy")
    if isinstance(policy, dict):
        target_class = policy.get("target_class")
        environment = policy.get("environment")
        if target_class in {"security", "production", "infrastructure"} or environment == "prod":
            return "high"
        if target_class == "general" and environment == "staging":
            return "medium"
    return "low"


def _policy_triggers(response: RunResponse) -> list[str]:
    decision = response.decision.model_dump() if hasattr(response.decision, "model_dump") else response.decision
    trace = decision.get("decision_trace", [])
    return [event.get("detail", "") for event in trace if event.get("stage") == "policy"]


def _intended_actions(response: RunResponse) -> list[str]:
    decision = response.decision.model_dump() if hasattr(response.decision, "model_dump") else response.decision
    target = decision.get("dispatch_target")
    if not isinstance(target, dict):
        return []
    procedure = target.get("procedure", "unknown_procedure")
    target_path = target.get("target", "unknown_target")
    return [f"{procedure}: {target_path}"]


def _expiry_for_status(status: str) -> str | None:
    if status != "PENDING_APPROVAL":
        return None
    return (datetime.now(UTC) + PENDING_APPROVAL_TTL).replace(microsecond=0).isoformat()


def expire_governed_request_if_needed(request_record: GovernedRequestRecord) -> GovernedRequestRecord:
    if request_record.status != "PENDING_APPROVAL" or not request_record.expires_at:
        return request_record

    try:
        expires_at = datetime.fromisoformat(request_record.expires_at)
    except ValueError:
        return request_record

    if expires_at > datetime.now(UTC):
        return request_record

    expired = request_record.model_copy(
        update={
            "status": "TERMINATED",
            "rejection_reason": request_record.rejection_reason or "Approval window expired before human decision.",
            "updated_at": datetime.now(UTC).isoformat(),
        }
    )
    upsert_governed_request(expired)
    return expired


def _partial_artifacts_from_execution(response: RunResponse) -> list[str]:
    if response.execution is None:
        return []
    execution = response.execution.model_dump() if hasattr(response.execution, "model_dump") else response.execution
    details = execution.get("details", {})
    completed = details.get("completed_artifacts")
    if isinstance(completed, list):
        return [str(item) for item in completed]
    artifacts = details.get("artifacts")
    if isinstance(artifacts, list):
        return [str(item) for item in artifacts]
    target = execution.get("target")
    return [str(target)] if target else []


def _tool_log_from_execution(response: RunResponse) -> list[dict[str, object]]:
    if response.execution is None:
        return []
    execution = response.execution.model_dump() if hasattr(response.execution, "model_dump") else response.execution
    details = execution.get("details", {})
    tool_call_log = details.get("tool_call_log")
    if isinstance(tool_call_log, list):
        return [dict(item) for item in tool_call_log if isinstance(item, dict)]
    return [
        {
            "step": execution.get("procedure"),
            "status": execution.get("status"),
            "target": execution.get("target"),
        }
    ]
