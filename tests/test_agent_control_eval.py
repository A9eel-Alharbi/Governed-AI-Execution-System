from __future__ import annotations

import unittest
from pathlib import Path

from agent_control_stack.eval import run_eval


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agent_control_stack" / "runtime" / "case_registry.yaml"
SCENARIOS = ROOT / "tests" / "scenarios" / "agent_control_scenarios.yaml"
OUTPUT_DIR = ROOT / "tests" / "_output" / "eval-test"


class AgentControlEvalTests(unittest.TestCase):
    def test_eval_summary_matches_current_scenarios(self) -> None:
        summary = run_eval(REGISTRY, SCENARIOS, OUTPUT_DIR)
        self.assertEqual(summary["total"], 24)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["passed"], 24)
        self.assertGreater(summary["safe_outcome_accuracy"], 0)
        self.assertIn("policy_critical_summary", summary)
        self.assertEqual(summary["policy_critical_summary"]["failed"], 0)
        self.assertIn("dispatch", summary["outcome_counts"])
        self.assertIn("category_summary", summary)
        self.assertIn("security", summary["category_summary"])
        self.assertIn("results", summary)


if __name__ == "__main__":
    unittest.main()
