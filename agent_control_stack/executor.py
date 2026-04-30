from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .models import DecisionEnvelope

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT / "_templates"


@dataclass
class ExecutionResult:
    procedure: str
    target: str
    status: str
    summary: str
    artifacts: list[str]
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionPlan:
    procedure: str
    target: str
    status: str
    summary: str
    artifacts: list[str]
    payload: dict[str, Any]
    write_operations: list[dict[str, str]]


class ExecutionError(ValueError):
    """Raised when a dispatch target cannot be executed safely."""


class ExecutionFailure(ExecutionError):
    """Raised when governed execution fails after planning has succeeded."""

    def __init__(
        self,
        message: str,
        *,
        last_successful_step: str | None = None,
        partial_artifacts: list[str] | None = None,
        tool_call_log: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.last_successful_step = last_successful_step
        self.partial_artifacts = partial_artifacts or []
        self.tool_call_log = tool_call_log or []


class GovernedExecutionPlanner:
    def plan(self, envelope: DecisionEnvelope, context: dict[str, Any] | None = None) -> ExecutionPlan:
        context = context or {}
        if envelope.outcome != "dispatch" or envelope.dispatch_target is None:
            raise ExecutionError("Only dispatch envelopes can be planned.")

        procedure = envelope.dispatch_target.procedure
        if procedure == "aos_quickstart_onboarding":
            return self._plan_onboard_new_project(envelope, context)
        if procedure == "draft_first_work_package":
            return self._plan_first_work_package(envelope, context)
        if procedure == "run_governed_work_package":
            return self._plan_run_governed_work_package(envelope, context)
        if procedure == "review_governed_work_package":
            return self._plan_review_governed_work_package(envelope, context)
        if procedure == "draft_followup_work_package":
            return self._plan_followup_work_package(envelope, context)
        if procedure == "open_constraint_change_request":
            return self._plan_constraint_change_request(envelope, context)
        if procedure == "prepare_constraint_update":
            return self._plan_constraint_update(envelope, context)
        if procedure == "run_aos_validation":
            return self._plan_aos_validation(envelope, context)
        if procedure == "escalate_protected_resource_change":
            return self._plan_protected_resource_escalation(envelope, context)
        raise ExecutionError(f"Unsupported procedure: {procedure}")

    def _plan_onboard_new_project(self, envelope: DecisionEnvelope, context: dict[str, Any]) -> ExecutionPlan:
        project_name = context.get("project_name", "Unnamed Project")
        project_goal = context.get("project_goal", "Goal not provided")
        v1_scope = context.get("v1_scope", "Scope not provided")
        repository_root = self._repository_root(context)
        output_dir = self._resolve_output_dir(context, repository_root, repository_root / "runtime-output" / "quickstart")
        constraints_dir = output_dir / "constraints"
        ops_dir = output_dir / "ops"
        today = datetime.now(timezone.utc).date().isoformat()

        vision_path = constraints_dir / "vision.md"
        schema_path = constraints_dir / "schema.md"
        api_contract_path = constraints_dir / "api-contract.md"
        security_rules_path = constraints_dir / "security-rules.md"
        vault_health_path = ops_dir / "vault-health.yaml"
        policy_profile_path = ops_dir / "policy-profile.yaml"

        vision_template = (TEMPLATES_DIR / "constraints" / "vision.md").read_text(encoding="utf-8")
        schema_template = (TEMPLATES_DIR / "constraints" / "schema.md").read_text(encoding="utf-8")
        api_template = (TEMPLATES_DIR / "constraints" / "api-contract.md").read_text(encoding="utf-8")
        security_template = (TEMPLATES_DIR / "constraints" / "security-rules.md").read_text(encoding="utf-8")

        vision_content = (
            vision_template
            .replace("`vision-core`", "`vision-agent-control-alpha`", 1)
            .replace("`[role and name]`", "`Product Lead`", 1)
            .replace("`YYYY-MM-DD`", f"`{today}`", 1)
            .replace("`Tier 1 | Tier 2 | Tier 3`", "`Tier 1`", 1)
            + f"\n\n## Draft Project Seed\n\n- Project name: `{project_name}`\n- Project goal: `{project_goal}`\n- Smallest v1 scope: `{v1_scope}`\n"
        )
        schema_content = (
            schema_template
            .replace("`schema-core`", "`schema-agent-control-alpha`", 1)
            .replace("`[backend lead or data owner]`", "`Backend Lead`", 1)
            .replace("`YYYY-MM-DD`", f"`{today}`", 1)
            .replace("`db/migrations/0001_init.sql`", "`db/migrations/0001_init.sql`", 1)
        )
        api_contract_content = (
            api_template
            .replace("`api-core`", "`api-agent-control-alpha`", 1)
            .replace("`[API owner]`", "`API Lead`", 1)
            .replace("`YYYY-MM-DD`", f"`{today}`", 1)
            .replace("`low` or `mixed`", "`mixed`", 1)
        )
        security_rules_content = (
            security_template
            .replace("`security-core`", "`security-agent-control-alpha`", 1)
            .replace("`[security owner or staff engineer]`", "`Security Lead`", 1)
            .replace("`YYYY-MM-DD`", f"`{today}`", 1)
        )
        policy_profile = yaml.safe_load((TEMPLATES_DIR / "ops" / "policy-profile.yaml").read_text(encoding="utf-8")) or {}
        policy_profile["last_validated"] = today
        vault_data = yaml.safe_load((TEMPLATES_DIR / "ops" / "vault-health.yaml").read_text(encoding="utf-8")) or {}
        vault_data["generated_at"] = f"{today}T00:00:00Z"
        vault_data["documents"] = [
            {
                "id": "vision-agent-control-alpha",
                "path": str(vision_path.relative_to(repository_root)).replace("\\", "/"),
                "owner": "Product Lead",
                "last_validated": today,
                "validation_method": "manual",
                "staleness_flag": "green",
                "wp_reference_count": 0,
                "open_conflicts": 0,
            },
            {
                "id": "schema-agent-control-alpha",
                "path": str(schema_path.relative_to(repository_root)).replace("\\", "/"),
                "owner": "Backend Lead",
                "last_validated": today,
                "validation_method": "manual",
                "staleness_flag": "green",
                "wp_reference_count": 0,
                "open_conflicts": 0,
            },
            {
                "id": "policy-agent-control-alpha",
                "path": str(policy_profile_path.relative_to(repository_root)).replace("\\", "/"),
                "owner": "Policy Admin",
                "last_validated": today,
                "validation_method": "automated",
                "staleness_flag": "green",
                "wp_reference_count": 0,
                "open_conflicts": 0,
            },
        ]

        return ExecutionPlan(
            procedure=envelope.dispatch_target.procedure,
            target=envelope.dispatch_target.target,
            status="written",
            summary=f"Generate AOS/CDD onboarding artifacts for {project_name}.",
            artifacts=[
                str(vision_path),
                str(schema_path),
                str(api_contract_path),
                str(security_rules_path),
                str(policy_profile_path),
                str(vault_health_path),
            ],
            payload={
                "project_name": project_name,
                "project_goal": project_goal,
                "v1_scope": v1_scope,
                "next_steps": [
                    "Define vision",
                    "Define schema source of truth",
                    "Define API contract source of truth",
                    "Define security rules",
                    "Record initial vault health",
                ],
            },
            write_operations=[
                {"type": "mkdir", "path": str(constraints_dir)},
                {"type": "mkdir", "path": str(ops_dir)},
                {"type": "write_text", "path": str(vision_path), "content": vision_content},
                {"type": "write_text", "path": str(schema_path), "content": schema_content},
                {"type": "write_text", "path": str(api_contract_path), "content": api_contract_content},
                {"type": "write_text", "path": str(security_rules_path), "content": security_rules_content},
                {"type": "write_text", "path": str(policy_profile_path), "content": yaml.safe_dump(policy_profile, sort_keys=False)},
                {"type": "write_text", "path": str(vault_health_path), "content": yaml.safe_dump(vault_data, sort_keys=False)},
            ],
        )

    def _plan_first_work_package(self, envelope: DecisionEnvelope, context: dict[str, Any]) -> ExecutionPlan:
        repository_root = self._repository_root(context)
        output_dir = self._resolve_output_dir(context, repository_root, repository_root / "runtime-output" / "work-packages")
        wp_id = str(context.get("wp_id", "WP-001"))
        output_path = output_dir / f"{wp_id}-draft.md"
        project_name = context.get("project_name", "Unnamed Project")
        project_goal = context.get("project_goal", "Goal not provided")
        first_scope = context.get("first_wp_scope", "Define the first bounded implementation task")
        today = datetime.now(timezone.utc).date().isoformat()
        template = (TEMPLATES_DIR / "work-packages" / "work-package.md").read_text(encoding="utf-8")
        content = (
            template
            .replace("WP-000", wp_id)
            .replace("[short action-oriented title]", f"Implement {first_scope}")
            .replace("[human owner]", "Platform Lead")
            .replace("YYYY-MM-DD", today, 1)
            .replace("[Jira/Linear/GitHub issue reference]", "ACS-DRAFT")
            .replace("draft | ready | in-progress | blocked | done", "draft")
            .replace("[explicit WP IDs or none]", "none", 2)
            .replace("high | low | mixed", "mixed", 1)
        )
        content += (
            f"\n## Draft Project Seed\n\n"
            f"- Project: `{project_name}`\n"
            f"- Goal: `{project_goal}`\n"
            f"- First scope: `{first_scope}`\n"
        )

        return ExecutionPlan(
            procedure=envelope.dispatch_target.procedure,
            target=envelope.dispatch_target.target,
            status="written",
            summary=f"Draft first work package scaffold at {output_path}.",
            artifacts=[str(output_path)],
            payload={"wp_id": wp_id, "project_name": project_name},
            write_operations=[
                {"type": "mkdir", "path": str(output_dir)},
                {"type": "write_text", "path": str(output_path), "content": content},
            ],
        )

    def _plan_run_governed_work_package(self, envelope: DecisionEnvelope, context: dict[str, Any]) -> ExecutionPlan:
        repository_root = self._repository_root(context)
        session_loader = self._resolve_repo_path(repository_root, context["session_loader"], "session_loader")
        if not session_loader.exists():
            raise ExecutionError(f"Session loader not found: {session_loader}")
        session_data = yaml.safe_load(session_loader.read_text(encoding="utf-8")) or {}
        constraints = [
            item["document"]
            for item in session_data.get("constraints_to_load", [])
            if isinstance(item, dict) and "document" in item
        ]
        policy_profile = session_data.get("policy_profile", {})
        return ExecutionPlan(
            procedure=envelope.dispatch_target.procedure,
            target=envelope.dispatch_target.target,
            status="ready",
            summary=f"Prepared governed execution plan for {session_data.get('work_package_id', 'unknown WP')}.",
            artifacts=[str(session_loader)],
            payload={
                "work_package_id": session_data.get("work_package_id"),
                "policy_profile": policy_profile,
                "constraints_to_load": constraints,
                "done_criteria_reference": session_data.get("done_criteria_reference"),
            },
            write_operations=[],
        )

    def _plan_review_governed_work_package(self, envelope: DecisionEnvelope, context: dict[str, Any]) -> ExecutionPlan:
        repository_root = self._repository_root(context)
        work_package = context.get("work_package")
        if not work_package:
            raise ExecutionError("Missing work_package context.")
        wp_path = self._resolve_repo_path(repository_root, work_package, "work_package")
        if not wp_path.exists():
            raise ExecutionError(f"Work package not found: {wp_path}")
        return ExecutionPlan(
            procedure=envelope.dispatch_target.procedure,
            target=envelope.dispatch_target.target,
            status="ready",
            summary=f"Prepared governed review plan for {wp_path.name}.",
            artifacts=[str(wp_path)],
            payload={
                "review_target": str(wp_path),
                "checks": [
                    "scope conformance",
                    "done criteria coverage",
                    "constraint loading review",
                ],
            },
            write_operations=[],
        )

    def _plan_followup_work_package(self, envelope: DecisionEnvelope, context: dict[str, Any]) -> ExecutionPlan:
        repository_root = self._repository_root(context)
        output_dir = self._resolve_output_dir(context, repository_root, repository_root / "runtime-output" / "work-packages")
        predecessor_wp = str(context.get("predecessor_wp"))
        if not predecessor_wp:
            raise ExecutionError("Missing predecessor_wp context.")
        wp_id = str(context.get("wp_id", "WP-002"))
        output_path = output_dir / f"{wp_id}-followup.md"
        today = datetime.now(timezone.utc).date().isoformat()
        template = (TEMPLATES_DIR / "work-packages" / "work-package.md").read_text(encoding="utf-8")
        followup_scope = str(context.get("followup_scope", "define the next bounded task after predecessor completion"))
        content = (
            template
            .replace("WP-000", wp_id)
            .replace("[short action-oriented title]", f"Follow up on {predecessor_wp}: {followup_scope}")
            .replace("[human owner]", "Platform Lead")
            .replace("YYYY-MM-DD", today, 1)
            .replace("[Jira/Linear/GitHub issue reference]", "ACS-FOLLOWUP")
            .replace("draft | ready | in-progress | blocked | done", "draft")
            .replace("[explicit WP IDs or none]", predecessor_wp, 1)
            .replace("[explicit WP IDs or none]", "none", 1)
            .replace("high | low | mixed", "mixed", 1)
        )
        return ExecutionPlan(
            procedure=envelope.dispatch_target.procedure,
            target=envelope.dispatch_target.target,
            status="written",
            summary=f"Draft follow-up work package at {output_path}.",
            artifacts=[str(output_path)],
            payload={"wp_id": wp_id, "predecessor_wp": predecessor_wp},
            write_operations=[
                {"type": "mkdir", "path": str(output_dir)},
                {"type": "write_text", "path": str(output_path), "content": content},
            ],
        )

    def _plan_constraint_change_request(self, envelope: DecisionEnvelope, context: dict[str, Any]) -> ExecutionPlan:
        repository_root = self._repository_root(context)
        output_dir = self._resolve_output_dir(context, repository_root, repository_root / "runtime-output" / "ccr")
        ccr_id = str(context.get("ccr_id", "CCR-001"))
        output_path = output_dir / f"{ccr_id}.yaml"
        now = datetime.now(timezone.utc).date().isoformat()
        payload = yaml.safe_load((TEMPLATES_DIR / "work-packages" / "constraint-change-request.yaml").read_text(encoding="utf-8")) or {}
        payload["ccr_id"] = ccr_id
        payload["date"] = now
        payload["author"] = str(context.get("author", "agent-control-stack"))
        payload["owner"] = str(context.get("owner", "Engineering Lead"))
        payload["last_validated"] = now
        payload["constraint_document"] = context.get("constraint_document", "unknown")
        payload["section_affected"] = str(context.get("section_affected", "unknown"))
        payload["summary"] = str(context.get("summary", "Constraint conflict reported by governed execution"))
        payload["reason"] = str(context.get("reason", "Constraint conflict reported by governed execution"))
        payload["approval_status"] = "draft"
        return ExecutionPlan(
            procedure=envelope.dispatch_target.procedure,
            target=envelope.dispatch_target.target,
            status="written",
            summary=f"Draft constraint change request at {output_path}.",
            artifacts=[str(output_path)],
            payload=dict(payload),
            write_operations=[
                {"type": "mkdir", "path": str(output_dir)},
                {"type": "write_text", "path": str(output_path), "content": yaml.safe_dump(payload, sort_keys=False)},
            ],
        )

    def _plan_constraint_update(self, envelope: DecisionEnvelope, context: dict[str, Any]) -> ExecutionPlan:
        repository_root = self._repository_root(context)
        constraint_document = context.get("constraint_document")
        if not constraint_document:
            raise ExecutionError("Missing constraint_document context.")
        target_path = self._resolve_repo_path(repository_root, constraint_document, "constraint_document")
        if not target_path.exists():
            raise ExecutionError(f"Constraint document not found: {target_path}")
        return ExecutionPlan(
            procedure=envelope.dispatch_target.procedure,
            target=envelope.dispatch_target.target,
            status="ready",
            summary=f"Prepared governed constraint-update plan for {target_path.name}.",
            artifacts=[str(target_path)],
            payload={
                "constraint_document": str(target_path),
                "required_followups": [
                    "review affected work packages",
                    "review session loaders",
                    "consider CCR if change is breaking",
                ],
            },
            write_operations=[],
        )

    def _plan_aos_validation(self, envelope: DecisionEnvelope, context: dict[str, Any]) -> ExecutionPlan:
        repository_root = self._repository_root(context)
        validator = self._resolve_repo_path(repository_root, "tools/aos_validate.py", "validator")
        if not validator.exists():
            raise ExecutionError(f"Validator not found: {validator}")
        return ExecutionPlan(
            procedure=envelope.dispatch_target.procedure,
            target=envelope.dispatch_target.target,
            status="ready",
            summary="Prepared AOS/CDD validation run plan.",
            artifacts=[str(validator)],
            payload={
                "command": "python tools\\aos_validate.py validate",
                "repository_root": str(repository_root),
            },
            write_operations=[],
        )

    def _plan_protected_resource_escalation(self, envelope: DecisionEnvelope, context: dict[str, Any]) -> ExecutionPlan:
        repository_root = self._repository_root(context)
        target = str(context.get("protected_target", envelope.dispatch_target.target))
        target_path = self._resolve_repo_path(repository_root, target, "protected_target")
        return ExecutionPlan(
            procedure=envelope.dispatch_target.procedure,
            target=envelope.dispatch_target.target,
            status="escalated",
            summary=f"Protected resource change requires elevated review for {target}.",
            artifacts=[str(target_path)],
            payload={
                "protected_target": target,
                "path_privilege": context.get("path_privilege"),
                "required_action": "human security review",
            },
            write_operations=[],
        )

    def _repository_root(self, context: dict[str, Any]) -> Path:
        repository_root = self._require_path(context, "repository_root").resolve()
        if not repository_root.exists():
            raise ExecutionError(f"repository_root not found: {repository_root}")
        return repository_root

    def _resolve_output_dir(self, context: dict[str, Any], repository_root: Path, default: Path) -> Path:
        candidate = context.get("output_dir", default)
        return self._resolve_repo_path(repository_root, candidate, "output_dir")

    def _resolve_repo_path(self, repository_root: Path, value: Any, label: str) -> Path:
        candidate = Path(str(value))
        if candidate.is_absolute():
            resolved = candidate.resolve()
        else:
            resolved = (repository_root / candidate).resolve()
        try:
            resolved.relative_to(repository_root)
        except ValueError as exc:
            raise ExecutionError(f"{label} must stay within repository_root: {resolved}") from exc
        return resolved

    def _require_path(self, context: dict[str, Any], key: str) -> Path:
        value = context.get(key)
        if not value:
            raise ExecutionError(f"Missing required path context: {key}")
        return Path(str(value))


class GovernedExecutor:
    def __init__(self, planner: GovernedExecutionPlanner | None = None) -> None:
        self._planner = planner or GovernedExecutionPlanner()

    def execute(self, envelope: DecisionEnvelope, context: dict[str, Any] | None = None) -> ExecutionResult:
        context = context or {}
        dry_run = self._is_dry_run(context)
        plan = self._planner.plan(envelope, context)
        if not plan.write_operations:
            return ExecutionResult(
                procedure=plan.procedure,
                target=plan.target,
                status=plan.status,
                summary=plan.summary,
                artifacts=plan.artifacts,
                payload={
                    **plan.payload,
                    "mode": "DRY_RUN" if dry_run else "LIVE",
                    "tool_call_log": [],
                },
            )

        skipped_writes: list[str] = []
        declared_writes: list[str] = []
        completed_artifacts: list[str] = []
        tool_call_log: list[dict[str, Any]] = []
        for index, operation in enumerate(plan.write_operations, start=1):
            op_type = operation["type"]
            path = Path(operation["path"])
            log_entry = {
                "step": index,
                "operation": op_type,
                "target": str(path),
                "status": "started",
            }
            tool_call_log.append(log_entry)
            try:
                if op_type == "mkdir":
                    self._ensure_directory(path, dry_run, skipped_writes, declared_writes, write_capability_declared=True)
                    log_entry["status"] = "skipped" if dry_run else "completed"
                    continue
                if op_type == "write_text":
                    self._write_text(path, operation["content"], dry_run, skipped_writes, declared_writes, write_capability_declared=True)
                    log_entry["status"] = "skipped" if dry_run else "completed"
                    if not dry_run:
                        completed_artifacts.append(str(path))
                    continue
                raise ExecutionError(f"Unsupported write operation: {op_type}")
            except Exception as exc:
                log_entry["status"] = "failed"
                log_entry["detail"] = str(exc)
                raise ExecutionFailure(
                    f"Execution failed during {op_type} for {path}",
                    last_successful_step=f"{op_type}_failed",
                    partial_artifacts=completed_artifacts.copy(),
                    tool_call_log=tool_call_log.copy(),
                ) from exc

        return ExecutionResult(
            procedure=plan.procedure,
            target=plan.target,
            status="simulated" if dry_run else "written",
            summary=(
                plan.summary.replace("Generate", "Would generate", 1)
                .replace("Draft", "Would draft", 1)
                if dry_run
                else plan.summary
            ),
            artifacts=plan.artifacts,
            payload={
                **plan.payload,
                "mode": "DRY_RUN" if dry_run else "LIVE",
                "skipped_writes": skipped_writes,
                "declared_writes": declared_writes,
                "completed_artifacts": completed_artifacts,
                "tool_call_log": tool_call_log,
                "write_enforcement_mode": "explicit",
            },
        )

    def _is_dry_run(self, context: dict[str, Any]) -> bool:
        return context.get("mode") == "DRY_RUN"

    def _ensure_directory(
        self,
        path: Path,
        dry_run: bool,
        skipped_writes: list[str],
        declared_writes: list[str],
        *,
        write_capability_declared: bool = False,
    ) -> None:
        action = f"mkdir:{path}"
        if write_capability_declared:
            declared_writes.append(action)
        if dry_run or not write_capability_declared:
            skipped_writes.append(f"would_{action}")
            return
        path.mkdir(parents=True, exist_ok=True)

    def _write_text(
        self,
        path: Path,
        content: str,
        dry_run: bool,
        skipped_writes: list[str],
        declared_writes: list[str],
        *,
        write_capability_declared: bool = False,
    ) -> None:
        action = f"write_text:{path}"
        if write_capability_declared:
            declared_writes.append(action)
        if dry_run or not write_capability_declared:
            skipped_writes.append(f"would_{action}")
            return
        path.write_text(content, encoding="utf-8")
