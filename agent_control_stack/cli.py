from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from .executor import GovernedExecutor
from .pipeline import AgentControlPipeline
from .store import FileSystemRunStore


DEFAULT_REGISTRY = Path("agent_control_stack") / "runtime" / "case_registry.yaml"


def load_context(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if "today" in data and isinstance(data["today"], str):
        data["today"] = date.fromisoformat(data["today"])
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the agent control stack pipeline.")
    parser.add_argument("--text", required=True, help="Raw user request to interpret")
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help="Path to the case registry YAML file",
    )
    parser.add_argument(
        "--context",
        type=Path,
        default=None,
        help="Optional YAML context for restoration, policy, and dispatch decisions",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the registered governed procedure after a dispatch decision",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Persist the decision and optional execution result to a local run store",
    )
    parser.add_argument(
        "--store-dir",
        type=Path,
        default=Path("runs"),
        help="Directory where persisted runs should be written",
    )
    args = parser.parse_args()

    pipeline = AgentControlPipeline.from_registry_file(args.registry)
    context = load_context(args.context)
    envelope = pipeline.decide(args.text, context)
    payload: dict[str, Any] = {"decision": envelope.to_dict()}
    execution_result = None
    if args.execute and envelope.outcome == "dispatch":
        execution_result = GovernedExecutor().execute(envelope, context)
        payload["execution"] = execution_result.to_dict()
    if args.persist:
        record = FileSystemRunStore(args.store_dir).persist(envelope, execution_result, context)
        payload["persistence"] = {
            "run_id": record.run_id,
            "decision_path": record.decision_path,
            "execution_path": record.execution_path,
        }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
