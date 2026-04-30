from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PLATFORM_API_ROOT = ROOT / "platform" / "api"

if str(PLATFORM_API_ROOT) not in sys.path:
    sys.path.insert(0, str(PLATFORM_API_ROOT))

from app.control import create_governed_request_record, dispatch_approved_governed_request
from app.models import ProjectRecord, RunRequest
from agent_control_stack.executor import ExecutionFailure


class PlatformRollbackTests(unittest.TestCase):
    def test_failed_execution_records_trace_and_remains_resubmittable(self) -> None:
        project = ProjectRecord(
            project_id="proj_rollback",
            owner_id="user_demo",
            owner_name="Demo User",
            name="Rollback Project",
            slug="rollback-project",
            repository_url="https://example.com/rollback-project",
            default_branch="main",
            status="active",
            repository_root=str(ROOT),
            default_context={"repository_root": str(ROOT)},
        )
        request = RunRequest(
            project_id=project.project_id,
            text="Create work package for the first implementation task",
            execute=True,
            persist=False,
            dry_run=False,
            context={"output_dir": str(ROOT / "tests" / "_output" / "rollback-path")},
        )

        _, governed_request = create_governed_request_record(project, request)
        self.assertEqual(governed_request.status, "PENDING_APPROVAL")

        approved = governed_request.model_copy(update={"status": "APPROVED"})
        with patch(
            "app.control.GovernedExecutor.execute",
            side_effect=ExecutionFailure(
                "simulated executor failure",
                last_successful_step="write_text_failed",
                partial_artifacts=["tests/_output/rollback-path/WP-001-draft.md.partial"],
                tool_call_log=[
                    {
                        "step": 1,
                        "operation": "write_text",
                        "target": "tests/_output/rollback-path/WP-001-draft.md",
                        "status": "failed",
                        "detail": "simulated executor failure",
                    }
                ],
            ),
        ):
            response, failed = dispatch_approved_governed_request(project, approved)

        self.assertIsNone(response)
        self.assertEqual(failed.status, "FAILED")
        self.assertEqual(failed.last_successful_step, "execution_failed")
        self.assertIn("ExecutionFailure", failed.failure_detail or "")
        self.assertEqual(failed.partial_artifacts, ["tests/_output/rollback-path/WP-001-draft.md.partial"])
        self.assertEqual(failed.tool_call_log[0]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
