from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from agent_control_stack.executor import GovernedExecutor
from agent_control_stack.executor import ExecutionError
from agent_control_stack.pipeline import AgentControlPipeline
from agent_control_stack.store import FileSystemRunStore


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agent_control_stack" / "runtime" / "case_registry.yaml"
TEST_OUTPUT = ROOT / "tests" / "_output"


class AgentControlPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        TEST_OUTPUT.mkdir(parents=True, exist_ok=True)

    def setUp(self) -> None:
        self.pipeline = AgentControlPipeline.from_registry_file(REGISTRY)
        self.executor = GovernedExecutor()

    def test_restoration_and_new_project_dispatch(self) -> None:
        envelope = self.pipeline.decide(
            "Start a new project in this repo tomorrow",
            {
                "today": date(2026, 4, 29),
                "repo_name": "aos-cdd-v2",
                "project_name": "Agent Control Stack",
                "project_goal": "build a governed agent system",
                "v1_scope": "constraint definition and first work package",
            },
        )
        self.assertEqual(envelope.outcome, "dispatch")
        self.assertEqual(envelope.case_id, "new_project.initial_definition")
        self.assertEqual(envelope.restored_input, "Start a new project in aos-cdd-v2 2026-04-30")
        self.assertTrue(envelope.dispatch_target)
        self.assertTrue(envelope.decision_trace)
        self.assertEqual(envelope.decision_trace[0].stage, "restore")

    def test_contradiction_refuses(self) -> None:
        envelope = self.pipeline.decide("Create billing and do not create billing")
        self.assertEqual(envelope.outcome, "refuse")
        self.assertEqual(envelope.refusal_reason, "Contradictory instruction for create: billing")
        self.assertEqual(envelope.decision_trace[-1].stage, "policy")

    def test_unregistered_case_refuses(self) -> None:
        envelope = self.pipeline.decide("Book a flight to Riyadh next week")
        self.assertEqual(envelope.outcome, "refuse")
        self.assertEqual(envelope.refusal_reason, "out_of_scope_case")

    def test_temporal_ambiguity_clarifies_when_unresolved(self) -> None:
        envelope = self.pipeline.decide("Start a new project in this repo next week")
        self.assertEqual(envelope.outcome, "clarify")
        self.assertIn("time reference", envelope.clarification_question)

    def test_run_wp_without_identifier_clarifies(self) -> None:
        envelope = self.pipeline.decide(
            "Run the work package now",
            {"repository_root": str(ROOT)},
        )
        self.assertEqual(envelope.outcome, "clarify")
        self.assertIn("Which work package", envelope.clarification_question)

    def test_constraint_conflict_without_target_clarifies(self) -> None:
        envelope = self.pipeline.decide(
            "Open a CCR now",
            {"repository_root": str(ROOT)},
        )
        self.assertEqual(envelope.outcome, "clarify")
        self.assertIn("constraint", envelope.clarification_question.lower())

    def test_missing_context_clarifies_for_run_wp(self) -> None:
        envelope = self.pipeline.decide(
            "Run WP-001 now",
            {"repository_root": str(ROOT)},
        )
        self.assertEqual(envelope.outcome, "clarify")
        self.assertEqual(envelope.case_id, "implementation.run_wp")
        self.assertIn("session_loader", envelope.clarification_question)

    def test_registered_run_wp_dispatches_with_required_context(self) -> None:
        envelope = self.pipeline.decide(
            "Run WP-001 now",
            {
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
            },
        )
        self.assertEqual(envelope.outcome, "dispatch")
        self.assertEqual(envelope.case_id, "implementation.run_wp")
        self.assertEqual(envelope.dispatch_target.procedure, "run_governed_work_package")

    def test_review_wp_dispatches(self) -> None:
        envelope = self.pipeline.decide(
            "Review WP-001",
            {
                "repository_root": str(ROOT),
                "work_package": "examples/agent-control-stack/work-packages/WP-001-decision-envelope-and-case-registry.md",
            },
        )
        self.assertEqual(envelope.outcome, "dispatch")
        self.assertEqual(envelope.case_id, "implementation.review_wp")

    def test_followup_wp_dispatches(self) -> None:
        envelope = self.pipeline.decide(
            "Create follow-up work package after WP-001",
            {
                "repository_root": str(ROOT),
                "predecessor_wp": "WP-001",
            },
        )
        self.assertEqual(envelope.outcome, "dispatch")
        self.assertEqual(envelope.case_id, "implementation.create_followup_wp")

    def test_validation_case_dispatches(self) -> None:
        envelope = self.pipeline.decide(
            "Run validation on this repo",
            {"repository_root": str(ROOT)},
        )
        self.assertEqual(envelope.outcome, "dispatch")
        self.assertEqual(envelope.case_id, "ops.run_validation")
        self.assertTrue(any(event.stage == "dispatch" for event in envelope.decision_trace))

    def test_constraint_update_dispatches(self) -> None:
        envelope = self.pipeline.decide(
            "Update constraints for the vision document",
            {
                "repository_root": str(ROOT),
                "constraint_document": "examples/agent-control-stack/constraints/vision.md",
            },
        )
        self.assertEqual(envelope.outcome, "dispatch")
        self.assertEqual(envelope.case_id, "docs.update_constraints")

    def test_security_target_class_requires_escalation(self) -> None:
        envelope = self.pipeline.decide(
            "Run validation on this repo",
            {
                "repository_root": str(ROOT),
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
            },
        )
        self.assertEqual(envelope.outcome, "escalate")
        self.assertEqual(envelope.escalation_reason, "policy_requires_escalation")

    def test_approval_artifact_can_authorize_scoped_security_validation(self) -> None:
        envelope = self.pipeline.decide(
            "Run validation on this repo",
            {
                "repository_root": str(ROOT),
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
                "approval_artifact": "examples/agent-control-stack/ops/APR-001-security-validation.yaml",
            },
        )
        self.assertEqual(envelope.outcome, "dispatch")
        self.assertEqual(envelope.case_id, "ops.run_validation")

    def test_invalid_policy_artifact_refuses(self) -> None:
        envelope = self.pipeline.decide(
            "Run WP-001 now",
            {
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                "policy_artifact": "examples/agent-control-stack/ops/missing-policy.yaml",
            },
        )
        self.assertEqual(envelope.outcome, "refuse")
        self.assertEqual(envelope.refusal_reason, "invalid_policy_artifact")

    def test_execute_new_project_onboarding(self) -> None:
        envelope = self.pipeline.decide(
            "Start a new project in this repo",
            {
                "repository_root": str(ROOT),
                "project_name": "Agent Control Stack",
                "project_goal": "build a governed agent system",
                "v1_scope": "first dispatchable alpha",
            },
        )
        output_dir = TEST_OUTPUT / "quickstart"
        output_dir.mkdir(parents=True, exist_ok=True)
        result = self.executor.execute(
            envelope,
            {
                "repository_root": str(ROOT),
                "output_dir": str(output_dir),
                "project_name": "Agent Control Stack",
                "project_goal": "build a governed agent system",
                "v1_scope": "first dispatchable alpha",
            },
        )
        self.assertEqual(result.status, "written")
        self.assertTrue(Path(result.artifacts[0]).exists())
        self.assertIn("Product Purpose", Path(result.artifacts[0]).read_text(encoding="utf-8"))

    def test_execute_create_first_wp_writes_draft(self) -> None:
        envelope = self.pipeline.decide(
            "Create work package for the first implementation task",
            {"repository_root": str(ROOT)},
        )
        output_dir = TEST_OUTPUT / "work-packages"
        output_dir.mkdir(parents=True, exist_ok=True)
        result = self.executor.execute(
            envelope,
            {
                "repository_root": str(ROOT),
                "output_dir": str(output_dir),
                "project_name": "Agent Control Stack",
                "project_goal": "build a governed agent system",
                "first_wp_scope": "implement the decision envelope",
            },
        )
        self.assertEqual(result.status, "written")
        draft_path = Path(result.artifacts[0])
        self.assertTrue(draft_path.exists())
        draft_text = draft_path.read_text(encoding="utf-8")
        self.assertIn("## Document Control", draft_text)
        self.assertIn("WP-001", draft_text)

    def test_execute_run_wp_returns_governed_plan(self) -> None:
        envelope = self.pipeline.decide(
            "Run WP-001 now",
            {
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
            },
        )
        result = self.executor.execute(
            envelope,
            {
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
            },
        )
        self.assertEqual(result.status, "ready")
        self.assertEqual(result.payload["work_package_id"], "WP-001")
        self.assertTrue(result.payload["constraints_to_load"])
        self.assertEqual(
            result.payload["policy_profile"]["document"],
            "examples/agent-control-stack/ops/policy-profile.yaml",
        )

    def test_execute_review_wp_returns_review_plan(self) -> None:
        envelope = self.pipeline.decide(
            "Review WP-001",
            {
                "repository_root": str(ROOT),
                "work_package": "examples/agent-control-stack/work-packages/WP-001-decision-envelope-and-case-registry.md",
            },
        )
        result = self.executor.execute(
            envelope,
            {
                "repository_root": str(ROOT),
                "work_package": "examples/agent-control-stack/work-packages/WP-001-decision-envelope-and-case-registry.md",
            },
        )
        self.assertEqual(result.status, "ready")
        self.assertIn("scope conformance", result.payload["checks"])

    def test_execute_followup_wp_writes_file(self) -> None:
        envelope = self.pipeline.decide(
            "Create follow-up work package after WP-001",
            {
                "repository_root": str(ROOT),
                "predecessor_wp": "WP-001",
            },
        )
        output_dir = TEST_OUTPUT / "followup-work-packages"
        output_dir.mkdir(parents=True, exist_ok=True)
        result = self.executor.execute(
            envelope,
            {
                "repository_root": str(ROOT),
                "predecessor_wp": "WP-001",
                "output_dir": str(output_dir),
            },
        )
        self.assertEqual(result.status, "written")
        self.assertTrue(Path(result.artifacts[0]).exists())

    def test_execute_constraint_change_request_writes_file(self) -> None:
        envelope = self.pipeline.decide(
            "Open a CCR for a constraint conflict",
            {"repository_root": str(ROOT)},
        )
        output_dir = TEST_OUTPUT / "ccr"
        output_dir.mkdir(parents=True, exist_ok=True)
        result = self.executor.execute(
            envelope,
            {
                "repository_root": str(ROOT),
                "output_dir": str(output_dir),
                "constraint_document": "examples/agent-control-stack/constraints/schema.md",
            },
        )
        self.assertEqual(result.status, "written")
        ccr_path = Path(result.artifacts[0])
        self.assertTrue(ccr_path.exists())
        ccr_text = ccr_path.read_text(encoding="utf-8")
        self.assertIn("ccr_id", ccr_text)
        self.assertIn("approval_status", ccr_text)

    def test_execute_validation_returns_plan(self) -> None:
        envelope = self.pipeline.decide(
            "Run validation on this repo",
            {"repository_root": str(ROOT)},
        )
        result = self.executor.execute(
            envelope,
            {"repository_root": str(ROOT)},
        )
        self.assertEqual(result.status, "ready")
        self.assertIn("aos_validate.py", result.artifacts[0])

    def test_execute_constraint_update_returns_plan(self) -> None:
        envelope = self.pipeline.decide(
            "Update constraints for the vision document",
            {
                "repository_root": str(ROOT),
                "constraint_document": "examples/agent-control-stack/constraints/vision.md",
            },
        )
        result = self.executor.execute(
            envelope,
            {
                "repository_root": str(ROOT),
                "constraint_document": "examples/agent-control-stack/constraints/vision.md",
            },
        )
        self.assertEqual(result.status, "ready")
        self.assertIn("required_followups", result.payload)

    def test_run_wp_rejects_session_loader_path_escape(self) -> None:
        envelope = self.pipeline.decide(
            "Run WP-001 now",
            {
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
            },
        )
        with self.assertRaises(ExecutionError):
            self.executor.execute(
                envelope,
                {
                    "repository_root": str(ROOT),
                    "session_loader": "..\\outside.yaml",
                },
            )

    def test_review_wp_rejects_work_package_path_escape(self) -> None:
        envelope = self.pipeline.decide(
            "Review WP-001",
            {
                "repository_root": str(ROOT),
                "work_package": "examples/agent-control-stack/work-packages/WP-001-decision-envelope-and-case-registry.md",
            },
        )
        with self.assertRaises(ExecutionError):
            self.executor.execute(
                envelope,
                {
                    "repository_root": str(ROOT),
                    "work_package": "..\\outside.md",
                },
            )

    def test_constraint_update_rejects_constraint_document_path_escape(self) -> None:
        envelope = self.pipeline.decide(
            "Update constraints for the vision document",
            {
                "repository_root": str(ROOT),
                "constraint_document": "examples/agent-control-stack/constraints/vision.md",
            },
        )
        with self.assertRaises(ExecutionError):
            self.executor.execute(
                envelope,
                {
                    "repository_root": str(ROOT),
                    "constraint_document": "..\\outside.md",
                },
            )

    def test_protected_resource_rejects_target_path_escape(self) -> None:
        envelope = self.pipeline.decide(
            "Modify .env secrets",
            {
                "repository_root": str(ROOT),
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
                "policy": {
                    "path_privilege": "security-approved",
                },
            },
        )
        with self.assertRaises(ExecutionError):
            self.executor.execute(
                envelope,
                {
                    "repository_root": str(ROOT),
                    "protected_target": "..\\..\\secret.env",
                },
            )

    def test_onboarding_rejects_output_dir_path_escape(self) -> None:
        envelope = self.pipeline.decide(
            "Start a new project in this repo",
            {
                "repository_root": str(ROOT),
                "project_name": "Agent Control Stack",
                "project_goal": "build a governed agent system",
                "v1_scope": "first dispatchable alpha",
            },
        )
        with self.assertRaises(ExecutionError):
            self.executor.execute(
                envelope,
                {
                    "repository_root": str(ROOT),
                    "output_dir": "C:\\Windows\\Temp\\acs",
                    "project_name": "Agent Control Stack",
                    "project_goal": "build a governed agent system",
                    "v1_scope": "first dispatchable alpha",
                },
            )

    def test_protected_resource_change_escalates_with_privilege(self) -> None:
        envelope = self.pipeline.decide(
            "Modify .env secrets",
            {
                "repository_root": str(ROOT),
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
                "policy": {
                    "path_privilege": "security-approved",
                },
            },
        )
        self.assertEqual(envelope.outcome, "dispatch")
        self.assertEqual(envelope.case_id, "security.protected_resource_change")
        result = self.executor.execute(
            envelope,
            {
                "repository_root": str(ROOT),
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
                "policy": {
                    "path_privilege": "security-approved",
                },
                "protected_target": ".env",
            },
        )
        self.assertEqual(result.status, "escalated")

    def test_protected_resource_fails_closed(self) -> None:
        envelope = self.pipeline.decide(
            "Run WP-001 and modify .env secrets",
            {
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
            },
        )
        self.assertEqual(envelope.outcome, "refuse")
        self.assertEqual(envelope.refusal_reason, "protected_resource_policy_missing")
        self.assertIn("Protected resource", envelope.decision_trace[-1].detail)

    def test_destructive_repo_path_fails_closed(self) -> None:
        envelope = self.pipeline.decide(
            "Delete files in the repo folder",
            {"repository_root": str(ROOT)},
        )
        self.assertEqual(envelope.outcome, "refuse")
        self.assertEqual(envelope.refusal_reason, "protected_resource_policy_missing")

    def test_schema_scope_contradiction_refuses(self) -> None:
        envelope = self.pipeline.decide("No schema changes, but add table subscriptions")
        self.assertEqual(envelope.outcome, "refuse")
        self.assertIn("schema scope", envelope.refusal_reason)

    def test_persisted_run_writes_decision_and_execution(self) -> None:
        envelope = self.pipeline.decide(
            "Run WP-001 now",
            {
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
            },
        )
        execution = self.executor.execute(
            envelope,
            {
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
            },
        )
        store_dir = TEST_OUTPUT / "runs"
        store_dir.mkdir(parents=True, exist_ok=True)
        record = FileSystemRunStore(store_dir).persist(
            envelope,
            execution,
            {
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
                "policy_artifact": "examples/agent-control-stack/ops/policy-profile.yaml",
            },
        )
        self.assertTrue(Path(record.decision_path).exists())
        self.assertTrue(Path(record.execution_path).exists())

    def test_decision_trace_serializes_in_payload(self) -> None:
        envelope = self.pipeline.decide(
            "Run WP-001 now",
            {
                "repository_root": str(ROOT),
                "session_loader": "examples/agent-control-stack/sessions/session-WP-001.yaml",
            },
        )
        payload = envelope.to_dict()
        self.assertIn("decision_trace", payload)
        self.assertTrue(payload["decision_trace"])


if __name__ == "__main__":
    unittest.main()
