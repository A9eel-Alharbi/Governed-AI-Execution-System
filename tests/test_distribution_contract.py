from __future__ import annotations

import importlib.resources as resources
import json
import unittest


class DistributionContractTests(unittest.TestCase):
    def test_case_registry_is_packaged(self) -> None:
        data = resources.files("agent_control_stack").joinpath("runtime/case_registry.yaml").read_text(encoding="utf-8")
        self.assertIn("new_project.initial_definition", data)
        self.assertIn("ops.run_validation", data)

    def test_policy_schema_is_packaged(self) -> None:
        raw = resources.files("agent_control_stack").joinpath("schemas/policy.schema.json").read_text(encoding="utf-8")
        schema = json.loads(raw)
        self.assertEqual(schema["title"], "Agent Control Stack Policy Context")
        self.assertIn("target_class", schema["properties"])

    def test_policy_profile_schema_is_packaged(self) -> None:
        raw = resources.files("agent_control_stack").joinpath("schemas/policy-profile.schema.json").read_text(encoding="utf-8")
        schema = json.loads(raw)
        self.assertEqual(schema["title"], "Policy Profile")
        self.assertIn("defaults", schema["properties"])

    def test_approval_record_schema_is_packaged(self) -> None:
        raw = resources.files("agent_control_stack").joinpath("schemas/approval-record.schema.json").read_text(encoding="utf-8")
        schema = json.loads(raw)
        self.assertEqual(schema["title"], "Approval Record")
        self.assertIn("policy_overlay", schema["properties"])

    def test_decision_schema_includes_decision_trace(self) -> None:
        raw = resources.files("agent_control_stack").joinpath("schemas/decision-envelope.schema.json").read_text(encoding="utf-8")
        schema = json.loads(raw)
        self.assertIn("decision_trace", schema["properties"])
        self.assertIn("decision_trace", schema["required"])


if __name__ == "__main__":
    unittest.main()
