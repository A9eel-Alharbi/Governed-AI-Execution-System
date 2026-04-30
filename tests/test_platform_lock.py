from __future__ import annotations

import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
PLATFORM_API_ROOT = ROOT / "platform" / "api"

if str(PLATFORM_API_ROOT) not in sys.path:
    sys.path.insert(0, str(PLATFORM_API_ROOT))

from app.main import app
from app.store import create_project, create_session_for_user, get_project_by_id, get_user_by_email, update_project
from app.models import ProjectRecord


class PlatformLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        user = get_user_by_email("demo@aos-cdd.local")
        assert user is not None
        cls.user = user
        cls.token = create_session_for_user(user)

    def _create_project(self, project_id: str, *, is_processing: bool = False, started_at: str | None = None) -> ProjectRecord:
        project = ProjectRecord(
            project_id=project_id,
            owner_id=self.user.user_id,
            owner_name=self.user.name,
            name=project_id,
            slug=project_id,
            repository_url=f"https://example.com/{project_id}",
            default_branch="main",
            status="active",
            repository_root=str(ROOT),
            default_context={"repository_root": str(ROOT)},
            is_processing=is_processing,
            processing_started_at=started_at,
        )
        try:
            return create_project(project)
        except Exception:
            return update_project(project)

    def test_execute_submit_rejects_when_project_lock_is_active(self) -> None:
        project = self._create_project(
            "proj_lock_active",
            is_processing=True,
            started_at=datetime.now(UTC).isoformat(),
        )
        response = self.client.post(
            "/requests/submit",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "project_id": project.project_id,
                "text": "Run WP-001 now",
                "execute": True,
                "persist": True,
                "dry_run": False,
                "context": {},
            },
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["detail"], "project_request_in_progress")

    def test_expired_lock_auto_releases_on_submit(self) -> None:
        project = self._create_project(
            "proj_lock_expired",
            is_processing=True,
            started_at=(datetime.now(UTC) - timedelta(hours=2)).isoformat(),
        )
        response = self.client.post(
            "/requests/submit",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "project_id": project.project_id,
                "text": "Create work package for the first implementation task",
                "execute": True,
                "persist": True,
                "dry_run": False,
                "context": {},
            },
        )
        self.assertEqual(response.status_code, 200)
        refreshed = get_project_by_id(project.project_id)
        self.assertIsNotNone(refreshed)
        assert refreshed is not None
        self.assertTrue(refreshed.is_processing)

    def test_force_unlock_clears_processing_flag(self) -> None:
        project = self._create_project(
            "proj_force_unlock",
            is_processing=True,
            started_at=datetime.now(UTC).isoformat(),
        )
        response = self.client.post(
            f"/projects/{project.project_id}/force-unlock",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response.status_code, 200)
        refreshed = get_project_by_id(project.project_id)
        self.assertIsNotNone(refreshed)
        assert refreshed is not None
        self.assertFalse(refreshed.is_processing)
        self.assertIsNone(refreshed.processing_started_at)


if __name__ == "__main__":
    unittest.main()
