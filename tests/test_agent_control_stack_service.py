from __future__ import annotations

import json
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from agent_control_stack.service import create_server


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agent_control_stack" / "runtime" / "case_registry.yaml"
TEST_OUTPUT = ROOT / "tests" / "_output"


class AgentControlServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        TEST_OUTPUT.mkdir(parents=True, exist_ok=True)
        cls.store_dir = TEST_OUTPUT / "service-runs"
        cls.store_dir.mkdir(parents=True, exist_ok=True)
        cls.server = create_server("127.0.0.1", 0, REGISTRY, cls.store_dir)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def test_interpret_and_persist(self) -> None:
        response = self._post(
            "/interpret",
            {
                "text": "Run WP-001 now",
                "context": {
                    "repository_root": str(ROOT),
                    "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                    "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
                },
                "execute": True,
                "persist": True,
            },
        )
        self.assertEqual(response["decision"]["outcome"], "dispatch")
        self.assertEqual(response["execution"]["status"], "ready")
        self.assertIn("run_id", response["persistence"])

        run_id = response["persistence"]["run_id"]
        stored = self._get(f"/runs/{run_id}")
        self.assertEqual(stored["decision"]["case_id"], "implementation.run_wp")
        self.assertEqual(stored["execution"]["status"], "ready")

    def test_interpret_clarify_returns_422(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self._post(
                "/interpret",
                {
                    "text": "Run WP-001 now",
                    "context": {"repository_root": str(ROOT)},
                },
            )
        self.assertEqual(ctx.exception.code, 422)
        payload = json.loads(ctx.exception.read().decode("utf-8"))
        ctx.exception.close()
        self.assertEqual(payload["decision"]["outcome"], "clarify")

    def test_execute_endpoint_runs_from_decision(self) -> None:
        decision = self._post(
            "/interpret",
            {
                "text": "Open a CCR for a constraint conflict",
                "context": {"repository_root": str(ROOT)},
            },
        )["decision"]
        response = self._post(
            "/execute",
            {
                "decision": decision,
                "context": {
                    "repository_root": str(ROOT),
                    "output_dir": str(TEST_OUTPUT / "service-ccr"),
                    "constraint_document": "examples/agent-control-stack/constraints/schema.md",
                },
            },
        )
        self.assertEqual(response["execution"]["status"], "written")

    def test_interpret_rejects_unknown_property(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self._post(
                "/interpret",
                {
                    "text": "Run WP-001 now",
                    "unexpected": True
                },
            )
        self.assertEqual(ctx.exception.code, 400)
        payload = json.loads(ctx.exception.read().decode("utf-8"))
        ctx.exception.close()
        self.assertEqual(payload["error"], "invalid_request")

    def test_interpret_rejects_invalid_policy(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self._post(
                "/interpret",
                {
                    "text": "Run validation on this repo",
                    "context": {
                        "repository_root": str(ROOT),
                        "policy": {
                            "environment": "moon"
                        }
                    }
                },
            )
        self.assertEqual(ctx.exception.code, 400)
        payload = json.loads(ctx.exception.read().decode("utf-8"))
        ctx.exception.close()
        self.assertEqual(payload["error"], "invalid_policy")

    def test_interpret_rejects_unsupported_media_type(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self._post_raw("/interpret", "{}", "text/plain")
        self.assertEqual(ctx.exception.code, 415)
        payload = json.loads(ctx.exception.read().decode("utf-8"))
        ctx.exception.close()
        self.assertEqual(payload["error"], "unsupported_media_type")

    def test_interpret_rejects_oversized_text(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self._post(
                "/interpret",
                {
                    "text": "x" * 4001,
                },
            )
        self.assertEqual(ctx.exception.code, 413)
        payload = json.loads(ctx.exception.read().decode("utf-8"))
        ctx.exception.close()
        self.assertEqual(payload["error"], "text_too_large")

    def test_interpret_rejects_oversized_request_body(self) -> None:
        oversized = {"text": "x", "context": {"padding": "y" * 70000}}
        with self.assertRaises(HTTPError) as ctx:
            self._post("/interpret", oversized)
        self.assertEqual(ctx.exception.code, 413)
        payload = json.loads(ctx.exception.read().decode("utf-8"))
        ctx.exception.close()
        self.assertEqual(payload["error"], "request_too_large")

    def test_interpret_refuses_invalid_policy_artifact(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self._post(
                "/interpret",
                {
                    "text": "Run WP-001 now",
                    "context": {
                        "repository_root": str(ROOT),
                        "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                        "policy_artifact": "examples/agent-control-stack/ops/missing-policy.yaml"
                    }
                },
            )
        self.assertEqual(ctx.exception.code, 403)
        payload = json.loads(ctx.exception.read().decode("utf-8"))
        ctx.exception.close()
        self.assertEqual(payload["decision"]["refusal_reason"], "invalid_policy_artifact")

    def test_execute_rejects_invalid_decision_shape(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self._post(
                "/execute",
                {
                    "decision": {
                        "outcome": "dispatch"
                    }
                },
            )
        self.assertEqual(ctx.exception.code, 400)
        payload = json.loads(ctx.exception.read().decode("utf-8"))
        ctx.exception.close()
        self.assertEqual(payload["error"], "invalid_decision")

    def _post(self, path: str, payload: dict[str, object]) -> dict[str, object]:
        return self._post_raw(path, json.dumps(payload), "application/json")

    def _post_raw(self, path: str, payload: str, content_type: str) -> dict[str, object]:
        request = Request(
            f"{self.base_url}{path}",
            data=payload.encode("utf-8"),
            headers={"Content-Type": content_type},
            method="POST",
        )
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))

    def _get(self, path: str) -> dict[str, object]:
        with urlopen(f"{self.base_url}{path}") as response:
            return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
