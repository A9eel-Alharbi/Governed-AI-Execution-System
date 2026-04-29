from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from .executor import GovernedExecutor
from .pipeline import AgentControlPipeline


DEFAULT_REGISTRY = Path("agent_control_stack") / "runtime" / "case_registry.yaml"
DEFAULT_SCENARIOS = Path("tests") / "scenarios" / "agent_control_scenarios.yaml"
DEFAULT_OUTPUT = Path("tests") / "_output" / "eval"


def run_eval(
    registry_path: str | Path = DEFAULT_REGISTRY,
    scenarios_path: str | Path = DEFAULT_SCENARIOS,
    output_root: str | Path = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    pipeline = AgentControlPipeline.from_registry_file(registry_path)
    executor = GovernedExecutor()
    scenarios = yaml.safe_load(Path(scenarios_path).read_text(encoding="utf-8"))["scenarios"]
    output_root = Path(output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    outcome_counts: Counter[str] = Counter()
    execution_status_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    category_pass_counts: Counter[str] = Counter()
    policy_critical_total = 0
    policy_critical_passed = 0
    passed = 0
    results: list[dict[str, Any]] = []

    for scenario in scenarios:
        context = dict(scenario.get("context", {}))
        category = str(scenario.get("category", "uncategorized"))
        policy_critical = bool(scenario.get("policy_critical", False))
        category_counts[category] += 1
        if scenario["expected"].get("execute"):
            context.setdefault("output_dir", str(output_root / scenario["id"]))

        envelope = pipeline.decide(scenario["text"], context)
        outcome_counts[envelope.outcome] += 1

        scenario_result: dict[str, Any] = {
            "id": scenario["id"],
            "category": category,
            "policy_critical": policy_critical,
            "outcome": envelope.outcome,
            "case_id": envelope.case_id,
            "passed": False,
        }

        success = envelope.outcome == scenario["expected"]["outcome"]
        expected_case_id = scenario["expected"].get("case_id")
        if expected_case_id is not None:
            success = success and envelope.case_id == expected_case_id

        if scenario["expected"].get("execute"):
            if envelope.outcome == "dispatch":
                execution = executor.execute(envelope, context)
                execution_status_counts[execution.status] += 1
                scenario_result["execution_status"] = execution.status
                success = success and execution.status == scenario["expected"]["execution_status"]
            else:
                scenario_result["execution_status"] = "not_executed"
                success = False

        scenario_result["passed"] = success
        if policy_critical:
            policy_critical_total += 1
        if success:
            passed += 1
            category_pass_counts[category] += 1
            if policy_critical:
                policy_critical_passed += 1
        results.append(scenario_result)

    category_summary: dict[str, Any] = {}
    for category, total in sorted(category_counts.items()):
        passed_count = category_pass_counts.get(category, 0)
        category_summary[category] = {
            "total": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "accuracy": round((passed_count / total) * 100, 1) if total else 0.0,
        }

    summary = {
        "total": len(scenarios),
        "passed": passed,
        "failed": len(scenarios) - passed,
        "safe_outcome_accuracy": round((passed / len(scenarios)) * 100, 1) if scenarios else 0.0,
        "policy_critical_summary": {
            "total": policy_critical_total,
            "passed": policy_critical_passed,
            "failed": policy_critical_total - policy_critical_passed,
            "accuracy": round((policy_critical_passed / policy_critical_total) * 100, 1) if policy_critical_total else 0.0,
        },
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "execution_status_counts": dict(sorted(execution_status_counts.items())),
        "category_summary": category_summary,
        "results": results,
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run scenario evals for the agent control stack.")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    summary = run_eval(args.registry, args.scenarios, args.output_dir)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
