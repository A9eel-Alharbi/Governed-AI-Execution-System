from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TEST_OUTPUT = ROOT / "tests" / "_output"
PLATFORM_API_ROOT = ROOT / "platform" / "api"

if str(PLATFORM_API_ROOT) not in sys.path:
    sys.path.insert(0, str(PLATFORM_API_ROOT))

from app.control import run_governed_request
from app.models import ProjectRecord, RunRequest


class PlatformControlDryRunTests(unittest.TestCase):
    def test_run_request_dry_run_propagates_to_executor(self) -> None:
        project = ProjectRecord(
            project_id="proj_dry_run",
            owner_id="user_demo",
            owner_name="Demo User",
            name="Dry Run Project",
            slug="dry-run-project",
            repository_url="https://example.com/dry-run-project",
            default_branch="main",
            status="active",
            repository_root=str(ROOT),
            default_context={"repository_root": str(ROOT)},
        )
        output_dir = TEST_OUTPUT / "platform-dry-run"
        response = run_governed_request(
            project,
            RunRequest(
                project_id=project.project_id,
                text="Create work package for the first implementation task",
                execute=True,
                persist=False,
                dry_run=True,
                context={"output_dir": str(output_dir)},
            ),
        )

        self.assertEqual(response.context["mode"], "DRY_RUN")
        self.assertIsNotNone(response.execution)
        self.assertEqual(response.execution.status, "simulated")
        self.assertFalse((output_dir / "WP-001-draft.md").exists())


if __name__ == "__main__":
    unittest.main()
