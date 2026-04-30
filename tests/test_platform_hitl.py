from __future__ import annotations

import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLATFORM_API_ROOT = ROOT / "platform" / "api"

if str(PLATFORM_API_ROOT) not in sys.path:
    sys.path.insert(0, str(PLATFORM_API_ROOT))

from app.control import expire_governed_request_if_needed
from app.models import GovernedRequestRecord


class PlatformHitlTests(unittest.TestCase):
    def test_pending_approval_expiry_terminates_request(self) -> None:
        record = GovernedRequestRecord(
            request_id="req_expired_hitl",
            project_id="proj_agent_control_stack",
            owner_id="user_demo",
            request_text="Run WP-001 now",
            status="PENDING_APPROVAL",
            dry_run=False,
            risk_level="high",
            outcome="dispatch",
            case_id="implementation.run_wp",
            policy_triggers=["Request approved for governed dispatch."],
            intended_actions=["run_governed_work_package: examples/agent-control-stack/sessions/session-WP-001.yaml"],
            request_context={},
            decision_trace=[],
            created_at=(datetime.now(UTC) - timedelta(hours=5)).isoformat(),
            updated_at=(datetime.now(UTC) - timedelta(hours=5)).isoformat(),
            expires_at=(datetime.now(UTC) - timedelta(minutes=1)).isoformat(),
        )

        expired = expire_governed_request_if_needed(record)
        self.assertEqual(expired.status, "TERMINATED")
        self.assertEqual(expired.rejection_reason, "Approval window expired before human decision.")

    def test_non_expired_pending_approval_stays_pending(self) -> None:
        record = GovernedRequestRecord(
            request_id="req_pending_hitl",
            project_id="proj_agent_control_stack",
            owner_id="user_demo",
            request_text="Run WP-001 now",
            status="PENDING_APPROVAL",
            dry_run=False,
            risk_level="high",
            outcome="dispatch",
            case_id="implementation.run_wp",
            policy_triggers=["Request approved for governed dispatch."],
            intended_actions=["run_governed_work_package: examples/agent-control-stack/sessions/session-WP-001.yaml"],
            request_context={},
            decision_trace=[],
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat(),
            expires_at=(datetime.now(UTC) + timedelta(hours=2)).isoformat(),
        )

        pending = expire_governed_request_if_needed(record)
        self.assertEqual(pending.status, "PENDING_APPROVAL")


if __name__ == "__main__":
    unittest.main()
