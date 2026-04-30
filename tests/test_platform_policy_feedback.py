from __future__ import annotations

import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLATFORM_API_ROOT = ROOT / "platform" / "api"

if str(PLATFORM_API_ROOT) not in sys.path:
    sys.path.insert(0, str(PLATFORM_API_ROOT))

from app.models import PolicyProfileRecord, PolicyProfileUpdateRequest, PolicyProfileVersionRecord
from app.store import (
    create_policy_profile_version,
    list_policy_profile_versions,
    next_policy_profile_version_id,
    upsert_policy_profile,
)


class PlatformPolicyFeedbackTests(unittest.TestCase):
    def test_policy_update_request_requires_reason(self) -> None:
        with self.assertRaises(Exception):
            PolicyProfileUpdateRequest(
                environment="dev",
                approval_state="unapproved",
                target_class="general",
                destructive_action=False,
                path_privilege=None,
                human_review_required=False,
                notes=[],
                reason="",
            )

    def test_policy_history_records_previous_and_new_state(self) -> None:
        project_id = "proj_policy_feedback_test"
        owner_id = "user_demo"
        before = PolicyProfileRecord(
            project_id=project_id,
            owner_id=owner_id,
            environment="dev",
            approval_state="unapproved",
            target_class="general",
            destructive_action=False,
            path_privilege=None,
            human_review_required=False,
            notes=["Initial state"],
            updated_at=datetime.now(UTC).isoformat(),
        )
        upsert_policy_profile(before)

        after = before.model_copy(
            update={
                "environment": "staging",
                "human_review_required": True,
                "notes": ["Manual review added after observing governed runs."],
                "updated_at": datetime.now(UTC).isoformat(),
            }
        )
        upsert_policy_profile(after)
        version = PolicyProfileVersionRecord(
            version_id=next_policy_profile_version_id(),
            project_id=project_id,
            owner_id=owner_id,
            previous_state=before.model_dump(),
            new_state=after.model_dump(),
            changed_by=owner_id,
            changed_at=after.updated_at,
            reason="Observed over-permissive behavior in staging review.",
        )
        create_policy_profile_version(version)

        history = list_policy_profile_versions(project_id, owner_id)
        self.assertTrue(history)
        latest = history[0]
        self.assertEqual(latest.reason, "Observed over-permissive behavior in staging review.")
        self.assertEqual(latest.changed_by, owner_id)
        self.assertEqual(latest.previous_state["environment"], "dev")
        self.assertEqual(latest.new_state["environment"], "staging")


if __name__ == "__main__":
    unittest.main()
