from __future__ import annotations

import unittest
from pathlib import Path

import yaml

from tools.aos_validate import ROOT, compare_session_policy_profile


class AosValidatePolicyEnforcementTests(unittest.TestCase):
    def test_agent_control_session_policy_profile_is_tracked(self) -> None:
        session_path = ROOT / "examples" / "agent-control-stack" / "sessions" / "session-WP-001.yaml"
        session_data = yaml.safe_load(session_path.read_text(encoding="utf-8"))
        errors = compare_session_policy_profile(ROOT, session_path, session_data)
        self.assertEqual(errors, [])

    def test_missing_policy_profile_in_vault_health_fails(self) -> None:
        session_path = ROOT / "examples" / "agent-control-stack" / "sessions" / "session-WP-001.yaml"
        session_data = yaml.safe_load(session_path.read_text(encoding="utf-8"))
        session_data["policy_profile"]["document"] = "examples/agent-control-stack/ops/not-tracked.yaml"
        errors = compare_session_policy_profile(ROOT, session_path, session_data)
        self.assertTrue(errors)
        self.assertIn("policy profile", errors[0].message.lower())


if __name__ == "__main__":
    unittest.main()
