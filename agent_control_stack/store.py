from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .executor import ExecutionResult
from .models import DecisionEnvelope
from .policy import PolicyResolutionError, load_policy_profile_from_context, resolve_policy_context

RUN_ID_PATTERN = re.compile(r"^run-\d{8}T\d{9,}Z$")
DEFAULT_RETENTION_DAYS = 30


@dataclass
class PersistenceRecord:
    run_id: str
    decision_path: str
    execution_path: str | None = None


class FileSystemRunStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def persist(
        self,
        decision: DecisionEnvelope,
        execution: ExecutionResult | None = None,
        context: dict[str, Any] | None = None,
    ) -> PersistenceRecord:
        context = context or {}
        profile = None
        try:
            profile = load_policy_profile_from_context(context)
            policy = resolve_policy_context(context, decision.case_id)
        except PolicyResolutionError:
            policy = resolve_policy_context({}, decision.case_id)
        persisted_at, retention_days, expires_at = build_retention_window(context)
        run_id = self._new_run_id()
        run_dir = self.root / run_id
        run_dir.mkdir(parents=True, exist_ok=False)

        decision_path = run_dir / "decision.json"
        decision_path.write_text(json.dumps(decision.to_dict(), indent=2), encoding="utf-8")

        execution_path: Path | None = None
        if execution is not None:
            execution_path = run_dir / "execution.json"
            execution_path.write_text(json.dumps(execution.to_dict(), indent=2), encoding="utf-8")

        summary_path = run_dir / "summary.json"
        policy_source = None
        if profile is not None and profile.source_path is not None:
            repository_root = context.get("repository_root")
            source_path = Path(profile.source_path)
            if repository_root:
                root_path = Path(str(repository_root))
                try:
                    policy_source = str(source_path.relative_to(root_path)).replace("\\", "/")
                except ValueError:
                    policy_source = str(source_path)
            else:
                policy_source = str(source_path)

        summary_payload: dict[str, Any] = {
            "run_id": run_id,
            "persisted_at": persisted_at.isoformat(),
            "retention_days": retention_days,
            "expires_at": expires_at.isoformat(),
            "outcome": decision.outcome,
            "case_id": decision.case_id,
            "has_execution": execution is not None,
            "environment": policy.environment,
            "approval_state": policy.approval_state,
            "target_class": policy.target_class,
            "destructive_action": policy.destructive_action,
            "path_privilege_present": policy.path_privilege is not None,
            "policy_source": policy_source,
            "human_review_gate": (
                decision.dispatch_target.human_review_gate if decision.dispatch_target is not None else None
            ),
            "dispatch_procedure": (
                decision.dispatch_target.procedure if decision.dispatch_target is not None else None
            ),
            "execution_status": execution.status if execution is not None else None,
        }
        summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

        return PersistenceRecord(
            run_id=run_id,
            decision_path=str(decision_path),
            execution_path=str(execution_path) if execution_path is not None else None,
        )

    def delete_expired_runs(self, now: datetime | None = None) -> list[str]:
        now = now or datetime.now(timezone.utc)
        deleted: list[str] = []
        for child in sorted(self.root.iterdir()):
            if not child.is_dir():
                continue
            summary_path = child / "summary.json"
            if not summary_path.exists():
                continue
            summary = self._read_json(summary_path)
            expires_at_text = summary.get("expires_at")
            if not isinstance(expires_at_text, str):
                continue
            expires_at = _parse_datetime(expires_at_text)
            if expires_at <= now:
                self._delete_run_dir(child)
                deleted.append(child.name)
        return deleted

    def load_run(self, run_id: str) -> dict[str, Any]:
        run_dir = self._resolve_run_dir(run_id)
        if not run_dir.exists():
            raise FileNotFoundError(run_id)

        payload: dict[str, Any] = {
            "run_id": run_id,
            "summary": self._read_json(run_dir / "summary.json"),
            "decision": self._read_json(run_dir / "decision.json"),
        }
        execution_path = run_dir / "execution.json"
        if execution_path.exists():
            payload["execution"] = self._read_json(execution_path)
        return payload

    def list_runs(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for child in sorted(self.root.iterdir()):
            if child.is_dir():
                summary_path = child / "summary.json"
                if summary_path.exists():
                    results.append(self._read_json(summary_path))
        return results

    def _new_run_id(self) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        return f"run-{timestamp}"

    def _read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _resolve_run_dir(self, run_id: str) -> Path:
        if not RUN_ID_PATTERN.match(run_id):
            raise FileNotFoundError(run_id)
        return self.root / run_id

    def _delete_run_dir(self, run_dir: Path) -> None:
        shutil.rmtree(run_dir)


def build_retention_window(context: dict[str, Any]) -> tuple[datetime, int, datetime]:
    retention_days = _normalize_retention_days(context.get("retention_days"))
    persisted_at = datetime.now(timezone.utc)
    expires_at = persisted_at + timedelta(days=retention_days)
    return persisted_at, retention_days, expires_at


def _normalize_retention_days(value: Any) -> int:
    if value is None:
        return DEFAULT_RETENTION_DAYS
    days = int(value)
    if days < 1 or days > 365:
        raise ValueError("retention_days must be between 1 and 365.")
    return days


def _parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
