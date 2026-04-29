from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_EVAL_REPORT = Path("reports") / "agent-control-eval.json"


class PolicyGateError(ValueError):
    """Raised when policy-aware quality gates fail."""


def enforce_policy_gate(
    eval_report_path: str | Path = DEFAULT_EVAL_REPORT,
    min_safe_outcome_accuracy: float = 100.0,
    min_policy_critical_accuracy: float = 100.0,
) -> dict[str, Any]:
    report_path = Path(eval_report_path)
    report = json.loads(_read_text_with_bom_fallback(report_path))

    failures: list[str] = []
    safe_accuracy = float(report.get("safe_outcome_accuracy", 0.0))
    if safe_accuracy < min_safe_outcome_accuracy:
        failures.append(
            f"safe_outcome_accuracy {safe_accuracy} below threshold {min_safe_outcome_accuracy}"
        )

    policy_summary = report.get("policy_critical_summary", {})
    policy_accuracy = float(policy_summary.get("accuracy", 0.0))
    policy_failed = int(policy_summary.get("failed", 0))
    if policy_accuracy < min_policy_critical_accuracy:
        failures.append(
            f"policy_critical_accuracy {policy_accuracy} below threshold {min_policy_critical_accuracy}"
        )
    if policy_failed > 0:
        failures.append(f"policy_critical scenarios failed: {policy_failed}")

    category_summary = report.get("category_summary", {})
    for category in ("security", "validation", "change-control"):
        category_report = category_summary.get(category)
        if isinstance(category_report, dict) and int(category_report.get("failed", 0)) > 0:
            failures.append(f"{category} category has failing scenarios")

    if failures:
        raise PolicyGateError("; ".join(failures))

    return {
        "status": "pass",
        "safe_outcome_accuracy": safe_accuracy,
        "policy_critical_accuracy": policy_accuracy,
        "policy_critical_total": int(policy_summary.get("total", 0)),
        "checked_report": str(report_path),
    }


def _read_text_with_bom_fallback(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce policy-aware CI gates from an eval report.")
    parser.add_argument("--eval-report", type=Path, default=DEFAULT_EVAL_REPORT)
    parser.add_argument("--min-safe-outcome-accuracy", type=float, default=100.0)
    parser.add_argument("--min-policy-critical-accuracy", type=float, default=100.0)
    args = parser.parse_args()

    result = enforce_policy_gate(
        eval_report_path=args.eval_report,
        min_safe_outcome_accuracy=args.min_safe_outcome_accuracy,
        min_policy_critical_accuracy=args.min_policy_critical_accuracy,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
