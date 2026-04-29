from __future__ import annotations

import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from agent_control_stack.pipeline import AgentControlPipeline
from agent_control_stack.store import FileSystemRunStore


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agent_control_stack" / "runtime" / "case_registry.yaml"
TEST_OUTPUT = ROOT / "tests" / "_output" / "store"


class AgentControlStoreTests(unittest.TestCase):
    def test_load_run_rejects_invalid_run_id_shape(self) -> None:
        store = FileSystemRunStore(TEST_OUTPUT)
        with self.assertRaises(FileNotFoundError):
            store.load_run("..\\..\\secrets")

    def test_load_run_accepts_persisted_run_id(self) -> None:
        pipeline = AgentControlPipeline.from_registry_file(REGISTRY)
        envelope = pipeline.decide("No schema changes, but add table subscriptions")
        store = FileSystemRunStore(TEST_OUTPUT)
        record = store.persist(envelope)

        payload = store.load_run(record.run_id)
        self.assertEqual(payload["run_id"], record.run_id)

    def test_persist_includes_retention_metadata(self) -> None:
        pipeline = AgentControlPipeline.from_registry_file(REGISTRY)
        envelope = pipeline.decide("No schema changes, but add table subscriptions")
        store = FileSystemRunStore(TEST_OUTPUT)
        record = store.persist(envelope, context={"retention_days": 7})

        payload = store.load_run(record.run_id)
        summary = payload["summary"]
        self.assertEqual(summary["retention_days"], 7)
        self.assertIn("expires_at", summary)

    def test_delete_expired_runs_removes_only_expired(self) -> None:
        pipeline = AgentControlPipeline.from_registry_file(REGISTRY)
        envelope = pipeline.decide("No schema changes, but add table subscriptions")
        store_dir = TEST_OUTPUT / f"retention-{uuid4().hex}"
        store = FileSystemRunStore(store_dir)

        expired = store.persist(envelope, context={"retention_days": 1})
        active = store.persist(envelope, context={"retention_days": 30})

        expired_payload = store.load_run(expired.run_id)
        active_payload = store.load_run(active.run_id)

        expired_summary = expired_payload["summary"]
        active_summary = active_payload["summary"]

        expired_path = store_dir / expired.run_id / "summary.json"
        active_path = store_dir / active.run_id / "summary.json"

        past = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        expired_summary["expires_at"] = past
        active_summary["expires_at"] = future
        expired_path.write_text(json.dumps(expired_summary, indent=2), encoding="utf-8")
        active_path.write_text(json.dumps(active_summary, indent=2), encoding="utf-8")

        with patch.object(store, "_delete_run_dir") as delete_run_dir:
            deleted = store.delete_expired_runs(now=datetime.now(timezone.utc))

        self.assertIn(expired.run_id, deleted)
        self.assertNotIn(active.run_id, deleted)
        delete_run_dir.assert_called_once()


if __name__ == "__main__":
    unittest.main()
