from __future__ import annotations

import unittest
from pathlib import Path
from uuid import uuid4

from agent_control_stack.eval import run_eval
from agent_control_stack.ops_report import build_run_report
from agent_control_stack.pipeline import AgentControlPipeline
from agent_control_stack.store import FileSystemRunStore


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agent_control_stack" / "runtime" / "case_registry.yaml"
SCENARIOS = ROOT / "tests" / "scenarios" / "agent_control_scenarios.yaml"
OUTPUT_DIR = ROOT / "tests" / "_output" / "ops-report"


class AgentControlOpsReportTests(unittest.TestCase):
    def test_report_aggregates_persisted_runs(self) -> None:
        store_dir = OUTPUT_DIR / f"runs-{uuid4().hex}"
        summary = run_eval(REGISTRY, SCENARIOS, OUTPUT_DIR / "eval")

        pipeline = AgentControlPipeline.from_registry_file(REGISTRY)
        store = FileSystemRunStore(store_dir)

        dispatch_envelope = pipeline.decide(
            "Run WP-001 now",
            {
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
            },
        )
        store.persist(
            dispatch_envelope,
            context={
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
            },
        )

        refuse_envelope = pipeline.decide("No schema changes, but add table subscriptions")
        store.persist(
            refuse_envelope,
            context={
                "policy": {
                    "environment": "prod",
                    "approval_state": "unapproved",
                    "target_class": "security",
                }
            },
        )

        report = build_run_report(store_dir)
        self.assertEqual(report["total_runs"], 2)
        self.assertEqual(report["active_runs"], 2)
        self.assertEqual(report["expired_runs"], 0)
        self.assertIn("dispatch", report["outcome_counts"])
        self.assertIn("refuse", report["outcome_counts"])
        self.assertIn("implementation.run_wp", report["case_counts"])
        self.assertIn("staging", report["environment_counts"])
        self.assertIn("security", report["target_class_counts"])
        self.assertIn("approved", report["approval_state_counts"])
        self.assertIn("examples/agent-control-stack/ops/policy-profile.yaml", report["policy_source_counts"])
        self.assertIn("30", report["retention_days_counts"])
        self.assertIn("schema scope", next(iter(report["refusal_reason_counts"])))
        self.assertEqual(summary["failed"], 0)


if __name__ == "__main__":
    unittest.main()
