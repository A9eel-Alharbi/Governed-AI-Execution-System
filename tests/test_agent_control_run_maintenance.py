from __future__ import annotations

import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from agent_control_stack.pipeline import AgentControlPipeline
from agent_control_stack.run_maintenance import _parse_datetime
from agent_control_stack.store import FileSystemRunStore


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agent_control_stack" / "runtime" / "case_registry.yaml"
OUTPUT_DIR = ROOT / "tests" / "_output" / "run-maintenance"


class AgentControlRunMaintenanceTests(unittest.TestCase):
    def test_dry_run_can_identify_expired_runs(self) -> None:
        store_dir = OUTPUT_DIR / f"store-{uuid4().hex}"
        pipeline = AgentControlPipeline.from_registry_file(REGISTRY)
        envelope = pipeline.decide("No schema changes, but add table subscriptions")
        store = FileSystemRunStore(store_dir)
        record = store.persist(envelope, context={"retention_days": 1})

        summary_path = store_dir / record.run_id / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["expires_at"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        listed = [item for item in store.list_runs() if _parse_datetime(item["expires_at"]) <= datetime.now(timezone.utc)]
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["run_id"], record.run_id)


if __name__ == "__main__":
    unittest.main()
