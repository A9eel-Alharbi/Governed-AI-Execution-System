from __future__ import annotations

import json
import unittest
from pathlib import Path

from agent_control_stack.eval import run_eval
from agent_control_stack.policy_gate import PolicyGateError, enforce_policy_gate


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agent_control_stack" / "runtime" / "case_registry.yaml"
SCENARIOS = ROOT / "tests" / "scenarios" / "agent_control_scenarios.yaml"
OUTPUT_DIR = ROOT / "tests" / "_output" / "policy-gate"


class AgentControlPolicyGateTests(unittest.TestCase):
    def test_policy_gate_passes_current_eval_report(self) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        summary = run_eval(REGISTRY, SCENARIOS, OUTPUT_DIR / "eval")
        report_path = OUTPUT_DIR / "agent-control-eval.json"
        report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        result = enforce_policy_gate(report_path)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["policy_critical_total"], summary["policy_critical_summary"]["total"])

    def test_policy_gate_fails_when_policy_critical_scenario_fails(self) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        report_path = OUTPUT_DIR / "agent-control-eval-fail.json"
        report = {
            "safe_outcome_accuracy": 95.0,
            "policy_critical_summary": {
                "total": 3,
                "passed": 2,
                "failed": 1,
                "accuracy": 66.7,
            },
            "category_summary": {
                "security": {"failed": 1},
                "validation": {"failed": 0},
                "change-control": {"failed": 0},
            },
        }
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

        with self.assertRaises(PolicyGateError):
            enforce_policy_gate(report_path)

    def test_policy_gate_reads_utf16_report(self) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        report_path = OUTPUT_DIR / "agent-control-eval-utf16.json"
        report = {
            "safe_outcome_accuracy": 100.0,
            "policy_critical_summary": {
                "total": 2,
                "passed": 2,
                "failed": 0,
                "accuracy": 100.0,
            },
            "category_summary": {
                "security": {"failed": 0},
                "validation": {"failed": 0},
                "change-control": {"failed": 0},
            },
        }
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-16")

        result = enforce_policy_gate(report_path)
        self.assertEqual(result["status"], "pass")


if __name__ == "__main__":
    unittest.main()
