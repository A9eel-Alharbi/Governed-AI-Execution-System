from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from agent_control_stack.executor import GovernedExecutor
from agent_control_stack.pipeline import AgentControlPipeline


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agent_control_stack" / "runtime" / "case_registry.yaml"
SCENARIOS = ROOT / "tests" / "scenarios" / "agent_control_scenarios.yaml"
OUTPUT_ROOT = ROOT / "tests" / "_output" / "scenarios"


class AgentControlScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        cls.pipeline = AgentControlPipeline.from_registry_file(REGISTRY)
        cls.executor = GovernedExecutor()
        cls.scenarios = yaml.safe_load(SCENARIOS.read_text(encoding="utf-8"))["scenarios"]

    def test_scenarios(self) -> None:
        for scenario in self.scenarios:
            with self.subTest(scenario=scenario["id"]):
                context = dict(scenario.get("context", {}))
                if scenario["expected"].get("execute"):
                    context.setdefault("output_dir", str(OUTPUT_ROOT / scenario["id"]))

                envelope = self.pipeline.decide(scenario["text"], context)

                self.assertEqual(envelope.outcome, scenario["expected"]["outcome"])
                expected_case_id = scenario["expected"].get("case_id")
                if expected_case_id is not None:
                    self.assertEqual(envelope.case_id, expected_case_id)

                if scenario["expected"].get("execute"):
                    execution = self.executor.execute(envelope, context)
                    self.assertEqual(execution.status, scenario["expected"]["execution_status"])
                    self.assertTrue(execution.artifacts)


if __name__ == "__main__":
    unittest.main()
