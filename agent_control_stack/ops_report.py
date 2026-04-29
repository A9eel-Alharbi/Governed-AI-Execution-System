from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .store import FileSystemRunStore


DEFAULT_RUNS = Path("runs")


def build_run_report(store_dir: str | Path = DEFAULT_RUNS) -> dict[str, Any]:
    store = FileSystemRunStore(store_dir)
    summaries = store.list_runs()

    outcome_counts: Counter[str] = Counter()
    case_counts: Counter[str] = Counter()
    execution_status_counts: Counter[str] = Counter()
    refusal_reason_counts: Counter[str] = Counter()
    escalation_reason_counts: Counter[str] = Counter()
    environment_counts: Counter[str] = Counter()
    target_class_counts: Counter[str] = Counter()
    approval_state_counts: Counter[str] = Counter()
    dispatch_procedure_counts: Counter[str] = Counter()
    human_review_gate_counts: Counter[str] = Counter()
    policy_source_counts: Counter[str] = Counter()
    expired_runs = 0
    active_runs = 0
    retention_days_counts: Counter[str] = Counter()

    runs: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    for summary in summaries:
        run_id = summary["run_id"]
        payload = store.load_run(run_id)
        decision = payload["decision"]
        outcome = str(decision["outcome"])
        outcome_counts[outcome] += 1

        case_id = decision.get("case_id")
        if case_id:
            case_counts[str(case_id)] += 1

        refusal_reason = decision.get("refusal_reason")
        if refusal_reason:
            refusal_reason_counts[str(refusal_reason)] += 1

        escalation_reason = decision.get("escalation_reason")
        if escalation_reason:
            escalation_reason_counts[str(escalation_reason)] += 1

        execution = payload.get("execution")
        execution_status = None
        if isinstance(execution, dict):
            execution_status = str(execution.get("status"))
            if execution_status:
                execution_status_counts[execution_status] += 1

        environment = summary.get("environment")
        if environment:
            environment_counts[str(environment)] += 1

        target_class = summary.get("target_class")
        if target_class:
            target_class_counts[str(target_class)] += 1

        approval_state = summary.get("approval_state")
        if approval_state:
            approval_state_counts[str(approval_state)] += 1

        dispatch_procedure = summary.get("dispatch_procedure")
        if dispatch_procedure:
            dispatch_procedure_counts[str(dispatch_procedure)] += 1

        human_review_gate = summary.get("human_review_gate")
        if human_review_gate is not None:
            human_review_gate_counts[str(bool(human_review_gate)).lower()] += 1

        policy_source = summary.get("policy_source")
        if policy_source:
            policy_source_counts[str(policy_source)] += 1

        retention_days = summary.get("retention_days")
        if retention_days is not None:
            retention_days_counts[str(retention_days)] += 1

        expires_at = summary.get("expires_at")
        expired = False
        if isinstance(expires_at, str):
            expired = _parse_report_datetime(expires_at) <= now
        if expired:
            expired_runs += 1
        else:
            active_runs += 1

        runs.append(
            {
                "run_id": run_id,
                "persisted_at": summary.get("persisted_at"),
                "outcome": outcome,
                "case_id": case_id,
                "execution_status": execution_status,
                "environment": environment,
                "target_class": target_class,
                "approval_state": approval_state,
                "policy_source": policy_source,
                "retention_days": retention_days,
                "expires_at": expires_at,
                "expired": expired,
            }
        )

    report = {
        "total_runs": len(summaries),
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "case_counts": dict(sorted(case_counts.items())),
        "execution_status_counts": dict(sorted(execution_status_counts.items())),
        "refusal_reason_counts": dict(sorted(refusal_reason_counts.items())),
        "escalation_reason_counts": dict(sorted(escalation_reason_counts.items())),
        "environment_counts": dict(sorted(environment_counts.items())),
        "target_class_counts": dict(sorted(target_class_counts.items())),
        "approval_state_counts": dict(sorted(approval_state_counts.items())),
        "dispatch_procedure_counts": dict(sorted(dispatch_procedure_counts.items())),
        "human_review_gate_counts": dict(sorted(human_review_gate_counts.items())),
        "policy_source_counts": dict(sorted(policy_source_counts.items())),
        "retention_days_counts": dict(sorted(retention_days_counts.items())),
        "active_runs": active_runs,
        "expired_runs": expired_runs,
        "runs": runs,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a machine-readable run report from persisted runs.")
    parser.add_argument("--store-dir", type=Path, default=DEFAULT_RUNS)
    args = parser.parse_args()

    report = build_run_report(args.store_dir)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def _parse_report_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
