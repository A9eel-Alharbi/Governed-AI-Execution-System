from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .models import BalancingEvent, DecisionEnvelope, DecisionEvent, DispatchTarget, RestorationEvent
from .policy import PolicyContext, PolicyResolutionError, resolve_policy_context
from .registry import CaseRegistry, RegisteredCase


PROTECTED_PATH_PATTERNS = (
    re.compile(r"\b(secrets?|\.env|private[_-]?key|credential|token)\b", re.IGNORECASE),
    re.compile(r"\b(/etc/|system32|\.git/|id_rsa)\b", re.IGNORECASE),
)

DESTRUCTIVE_ACTION_PATTERNS = (
    re.compile(r"\b(delete|remove|wipe|destroy)\b", re.IGNORECASE),
    re.compile(r"\b(reset|format)\b", re.IGNORECASE),
)

AMBIGUOUS_REFERENCE_PATTERNS = (
    re.compile(r"\b(it|that|this|them|those)\b", re.IGNORECASE),
    re.compile(r"\b(here|there)\b", re.IGNORECASE),
)

TEMPORAL_AMBIGUITY_PATTERNS = (
    re.compile(r"\b(tomorrow|next week|later|soon|after that)\b", re.IGNORECASE),
    re.compile(r"\b(today|yesterday)\b", re.IGNORECASE),
)


class ContradictionError(ValueError):
    """Raised when the request contains incompatible instructions."""


class AgentControlPipeline:
    def __init__(self, registry: CaseRegistry) -> None:
        self._registry = registry

    @classmethod
    def from_registry_file(cls, path: str | Path) -> "AgentControlPipeline":
        return cls(CaseRegistry.from_yaml(Path(path)))

    def decide(self, raw_input: str, context: dict[str, Any] | None = None) -> DecisionEnvelope:
        context = context or {}
        restored_input, restoration_trace = self._restore(raw_input, context)
        decision_trace: list[DecisionEvent] = []
        if restoration_trace:
            decision_trace.append(DecisionEvent(stage="restore", detail=f"Applied {len(restoration_trace)} restoration step(s)."))
        else:
            decision_trace.append(DecisionEvent(stage="restore", detail="No restoration changes were applied."))
        try:
            normalized_input, balancing_trace = self._balance(restored_input, context)
        except ContradictionError as exc:
            return DecisionEnvelope(
                raw_input=raw_input,
                restored_input=restored_input,
                normalized_input=restored_input,
                outcome="refuse",
                rationale="The request is internally contradictory.",
                refusal_reason=str(exc),
                restoration_trace=restoration_trace,
                balancing_trace=[BalancingEvent(kind="contradiction", detail=str(exc))],
                decision_trace=decision_trace + [
                    DecisionEvent(stage="balance", detail="Balancing detected a contradiction."),
                    DecisionEvent(stage="policy", detail="Request refused because the input is contradictory."),
                ],
            )
        if balancing_trace:
            decision_trace.append(DecisionEvent(stage="balance", detail=f"Applied {len(balancing_trace)} balancing step(s)."))
        else:
            decision_trace.append(DecisionEvent(stage="balance", detail="No balancing changes were applied."))

        case_id = self._classify(normalized_input)
        if case_id is None:
            return DecisionEnvelope(
                raw_input=raw_input,
                restored_input=restored_input,
                normalized_input=normalized_input,
                outcome="refuse",
                rationale="The request does not match a registered case family.",
                refusal_reason="out_of_scope_case",
                restoration_trace=restoration_trace,
                balancing_trace=balancing_trace,
                decision_trace=decision_trace + [
                    DecisionEvent(stage="classify", detail="No registered case matched the request."),
                    DecisionEvent(stage="policy", detail="Request refused because it is out of scope."),
                ],
            )
        decision_trace.append(DecisionEvent(stage="classify", detail=f"Matched case `{case_id}`."))

        try:
            policy = resolve_policy_context(context, case_id)
        except PolicyResolutionError as exc:
            return DecisionEnvelope(
                raw_input=raw_input,
                restored_input=restored_input,
                normalized_input=normalized_input,
                outcome="refuse",
                case_id=case_id,
                rationale="The request cannot proceed because the governing policy artifact is invalid or incomplete.",
                refusal_reason="invalid_policy_artifact",
                restoration_trace=restoration_trace,
                balancing_trace=balancing_trace,
                decision_trace=decision_trace + [
                    DecisionEvent(stage="policy", detail=str(exc)),
                ],
            )

        ambiguity_question = self._ambiguity_question(case_id, normalized_input, context)
        if ambiguity_question is not None:
            return DecisionEnvelope(
                raw_input=raw_input,
                restored_input=restored_input,
                normalized_input=normalized_input,
                outcome="clarify",
                case_id=case_id,
                rationale="The request contains unresolved ambiguity that should be clarified before dispatch.",
                clarification_question=ambiguity_question,
                restoration_trace=restoration_trace,
                balancing_trace=balancing_trace,
                decision_trace=decision_trace + [
                    DecisionEvent(stage="ambiguity", detail=ambiguity_question),
                    DecisionEvent(stage="policy", detail="Request requires clarification before dispatch."),
                ],
            )

        clarification_question = self._clarification_question(case_id, normalized_input, context)
        if clarification_question is not None:
            return DecisionEnvelope(
                raw_input=raw_input,
                restored_input=restored_input,
                normalized_input=normalized_input,
                outcome="clarify",
                case_id=case_id,
                rationale="The request maps to a known case, but required intent is still missing.",
                clarification_question=clarification_question,
                restoration_trace=restoration_trace,
                balancing_trace=balancing_trace,
                decision_trace=decision_trace + [
                    DecisionEvent(stage="clarification", detail=clarification_question),
                    DecisionEvent(stage="policy", detail="Request requires additional context before dispatch."),
                ],
            )

        registered_case = self._registry.get(case_id)
        if registered_case is None:
            return DecisionEnvelope(
                raw_input=raw_input,
                restored_input=restored_input,
                normalized_input=normalized_input,
                outcome="escalate",
                case_id=case_id,
                rationale="The request classified into a case with no registered procedure.",
                escalation_reason="missing_case_registration",
                restoration_trace=restoration_trace,
                balancing_trace=balancing_trace,
                decision_trace=decision_trace + [
                    DecisionEvent(stage="dispatch", detail="Case has no registered procedure."),
                    DecisionEvent(stage="policy", detail="Request escalated due to missing case registration."),
                ],
            )
        decision_trace.append(
            DecisionEvent(
                stage="dispatch",
                detail=f"Resolved procedure `{registered_case.procedure}` targeting `{registered_case.target}`.",
            )
        )

        if self._mentions_protected_resource(normalized_input) and not policy.allows_protected_change():
            return DecisionEnvelope(
                raw_input=raw_input,
                restored_input=restored_input,
                normalized_input=normalized_input,
                outcome="refuse",
                case_id=case_id,
                rationale="The request mentions a protected resource without the required policy dimension.",
                refusal_reason="protected_resource_policy_missing",
                restoration_trace=restoration_trace,
                balancing_trace=balancing_trace,
                decision_trace=decision_trace + [
                    DecisionEvent(stage="policy", detail="Protected resource detected without sufficient approval or privilege context."),
                ],
            )

        if policy.requires_escalation() and case_id != "security.protected_resource_change":
            return DecisionEnvelope(
                raw_input=raw_input,
                restored_input=restored_input,
                normalized_input=normalized_input,
                outcome="escalate",
                case_id=case_id,
                rationale="The request targets a higher-risk class and requires explicit escalation.",
                escalation_reason="policy_requires_escalation",
                restoration_trace=restoration_trace,
                balancing_trace=balancing_trace,
                decision_trace=decision_trace + [
                    DecisionEvent(
                        stage="policy",
                        detail=f"Escalation required for target_class `{policy.target_class}` in environment `{policy.environment}`.",
                    ),
                ],
            )

        missing_context = [item for item in registered_case.required_context if not self._has_required_context(item, context, policy)]
        if missing_context:
            return DecisionEnvelope(
                raw_input=raw_input,
                restored_input=restored_input,
                normalized_input=normalized_input,
                outcome="clarify",
                case_id=case_id,
                rationale="The case is registered, but required execution context is missing.",
                clarification_question=f"Provide the missing execution context: {', '.join(missing_context)}.",
                restoration_trace=restoration_trace,
                balancing_trace=balancing_trace,
                decision_trace=decision_trace + [
                    DecisionEvent(
                        stage="policy",
                        detail=f"Missing required execution context: {', '.join(missing_context)}.",
                    ),
                ],
            )

        return DecisionEnvelope(
            raw_input=raw_input,
            restored_input=restored_input,
            normalized_input=normalized_input,
            outcome="dispatch",
            case_id=case_id,
            rationale="The request is clear enough to proceed through a registered governed path.",
            restoration_trace=restoration_trace,
            balancing_trace=balancing_trace,
            decision_trace=decision_trace + [
                DecisionEvent(stage="policy", detail="Request approved for governed dispatch."),
            ],
            dispatch_target=DispatchTarget(
                case_id=registered_case.case_id,
                procedure=registered_case.procedure,
                target=registered_case.target,
                human_review_gate=registered_case.human_review_gate,
            ),
        )

    def _restore(self, raw_input: str, context: dict[str, Any]) -> tuple[str, list[RestorationEvent]]:
        restored = raw_input
        trace: list[RestorationEvent] = []

        today_value = context.get("today")
        if isinstance(today_value, date) and "tomorrow" in restored.lower():
            replacement = (today_value + timedelta(days=1)).isoformat()
            restored = re.sub(r"\btomorrow\b", replacement, restored, flags=re.IGNORECASE)
            trace.append(
                RestorationEvent(
                    source="tomorrow",
                    replacement=replacement,
                    reason="Resolved relative date from supplied context.",
                )
            )

        repo_name = context.get("repo_name")
        if repo_name and re.search(r"\bthis repo\b", restored, re.IGNORECASE):
            restored = re.sub(r"\bthis repo\b", str(repo_name), restored, flags=re.IGNORECASE)
            trace.append(
                RestorationEvent(
                    source="this repo",
                    replacement=str(repo_name),
                    reason="Expanded repository reference from supplied context.",
                )
            )

        for alias, canonical in context.get("aliases", {}).items():
            pattern = re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)
            if pattern.search(restored):
                restored = pattern.sub(str(canonical), restored)
                trace.append(
                    RestorationEvent(
                        source=str(alias),
                        replacement=str(canonical),
                        reason="Expanded explicit alias mapping from context.",
                    )
                )

        return restored, trace

    def _balance(self, restored_input: str, context: dict[str, Any]) -> tuple[str, list[BalancingEvent]]:
        normalized = " ".join(restored_input.split())
        trace: list[BalancingEvent] = []

        aliases = context.get("normalize_aliases", {})
        for alias, canonical in aliases.items():
            pattern = re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)
            if pattern.search(normalized):
                normalized = pattern.sub(str(canonical), normalized)
                trace.append(
                    BalancingEvent(
                        kind="alias_normalized",
                        detail=f"{alias} -> {canonical}",
                    )
                )

        contradiction = self._detect_contradiction(normalized)
        if contradiction is not None:
            raise ContradictionError(contradiction)

        return normalized, trace

    def _detect_contradiction(self, text: str) -> str | None:
        lowered = text.lower()
        for verb in ("create", "build", "delete", "send", "change", "modify", "run", "open"):
            positive = self._extract_verb_targets(lowered, verb)
            negative = self._extract_verb_targets(lowered, verb, negated=True)
            overlap = sorted(set(positive).intersection(negative))
            if overlap:
                return f"Contradictory instruction for {verb}: {', '.join(overlap)}"

        if "with no ui" in lowered and any(token in lowered for token in ("build ui", "create ui", "add ui")):
            return "Contradictory instruction for ui scope: request both includes and excludes UI work"
        if "no schema changes" in lowered and any(
            token in lowered for token in ("change schema", "rename column", "add table", "modify schema")
        ):
            return "Contradictory instruction for schema scope: request both forbids and requires schema changes"
        return None

    def _extract_verb_targets(self, text: str, verb: str, negated: bool = False) -> list[str]:
        prefix = r"do not\s+" if negated else ""
        patterns = (
            re.compile(rf"\b{prefix}{verb}\s+([a-z0-9_./-]+)", re.IGNORECASE),
            re.compile(rf"\b{prefix}{verb}\s+(?:the\s+)?([a-z0-9_./-]+)\b", re.IGNORECASE),
            re.compile(rf"\b{prefix}{verb}\s+([a-z0-9_./-]+)\s+endpoint\b", re.IGNORECASE),
        )
        results: list[str] = []
        for pattern in patterns:
            results.extend(match.strip(" .,!?:;") for match in pattern.findall(text))
        return results

    def _classify(self, normalized_input: str) -> str | None:
        lowered = normalized_input.lower()
        if any(token in lowered for token in ("new project", "empty folder", "start a project", "quickstart")):
            return "new_project.initial_definition"
        if "review wp" in lowered or "review work package" in lowered or "review the work package" in lowered or "review wp-" in lowered:
            return "implementation.review_wp"
        if (
            "follow-up wp" in lowered
            or "followup wp" in lowered
            or "create follow-up work package" in lowered
            or "create a follow-up work package" in lowered
        ):
            return "implementation.create_followup_wp"
        if "first wp" in lowered or "create work package" in lowered:
            return "implementation.create_first_wp"
        if (
            re.search(r"\bwp-\d+\b", lowered)
            or "run wp" in lowered
            or "implement wp" in lowered
            or "run work package" in lowered
            or "run the work package" in lowered
        ):
            return "implementation.run_wp"
        if "validate repo" in lowered or "run validation" in lowered or "validate aos" in lowered:
            return "ops.run_validation"
        if (
            "update constraint" in lowered
            or "update constraints" in lowered
            or "revise vision" in lowered
            or "revise the vision constraint" in lowered
            or "revise the vision constraints" in lowered
        ):
            return "docs.update_constraints"
        if self._mentions_protected_resource(lowered) and any(
            token in lowered for token in ("change", "modify", "edit", "update", "delete", "remove")
        ):
            return "security.protected_resource_change"
        if "constraint conflict" in lowered or "ccr" in lowered or "change control" in lowered:
            return "change.constraint_conflict"
        return None

    def _ambiguity_question(
        self,
        case_id: str,
        normalized_input: str,
        context: dict[str, Any],
    ) -> str | None:
        lowered = normalized_input.lower()

        if self._has_temporal_ambiguity(lowered, context):
            return "Clarify the intended time reference before proceeding."

        if case_id == "implementation.run_wp":
            if "wp-" not in lowered:
                return "Which work package should be executed?"
            if self._has_ambiguous_reference(lowered) and "this repo" not in lowered and not context.get("referent"):
                return "Clarify what object or target the work-package request refers to."

        if case_id == "implementation.review_wp":
            if "wp-" not in lowered and not context.get("work_package"):
                return "Which work package should be reviewed?"

        if case_id == "implementation.create_followup_wp":
            if "wp-" not in lowered and not context.get("predecessor_wp"):
                return "Which completed or in-flight work package should the follow-up depend on?"

        if case_id == "implementation.create_first_wp":
            if not any(token in lowered for token in ("first", "initial", "implementation", "endpoint", "schema", "feature")):
                return "Clarify the bounded implementation scope for the first work package."

        if case_id == "change.constraint_conflict":
            if "constraint" not in lowered and not context.get("constraint_document"):
                return "Which constraint document or governed surface is in conflict?"

        if case_id == "docs.update_constraints":
            if not context.get("constraint_document"):
                return "Which constraint document should be updated?"

        if case_id == "security.protected_resource_change":
            if self._has_ambiguous_reference(lowered) and not context.get("protected_target"):
                return "Which protected file, secret, or governed target should be changed?"

        if case_id == "new_project.initial_definition":
            if self._has_ambiguous_reference(lowered) and not context.get("project_name"):
                return "Clarify what project or repository target should be initialized."

        return None

    def _clarification_question(
        self,
        case_id: str,
        normalized_input: str,
        context: dict[str, Any],
    ) -> str | None:
        lowered = normalized_input.lower()
        if case_id == "new_project.initial_definition":
            missing = []
            if not context.get("project_name") and not any(token in lowered for token in ("project", "app", "api", "tool", "system")):
                missing.append("project name")
            if not context.get("project_goal") and not any(word in lowered for word in ("build", "app", "api", "system", "tool")):
                missing.append("product goal")
            if "v1" not in lowered and not context.get("v1_scope"):
                missing.append("smallest v1 scope")
            if missing:
                return f"Before onboarding, clarify the following: {', '.join(missing)}."
        if case_id == "implementation.review_wp":
            if not context.get("work_package") and "wp-" not in lowered:
                return "Provide the work-package identifier to review."
        if case_id == "implementation.create_followup_wp":
            if not context.get("predecessor_wp") and "wp-" not in lowered:
                return "Provide the predecessor work-package identifier for the follow-up draft."
        if case_id == "docs.update_constraints":
            if not context.get("constraint_document"):
                return "Provide the constraint document path that should be updated."
        return None

    def _mentions_protected_resource(self, normalized_input: str) -> bool:
        if any(pattern.search(normalized_input) for pattern in PROTECTED_PATH_PATTERNS):
            return True
        return self._looks_like_destructive_path_operation(normalized_input)

    def _has_ambiguous_reference(self, lowered: str) -> bool:
        return any(pattern.search(lowered) for pattern in AMBIGUOUS_REFERENCE_PATTERNS)

    def _has_temporal_ambiguity(self, lowered: str, context: dict[str, Any]) -> bool:
        if context.get("today") is not None:
            unresolved = tuple(pattern.pattern for pattern in TEMPORAL_AMBIGUITY_PATTERNS[:1])
            return any(re.search(pattern, lowered, re.IGNORECASE) for pattern in unresolved)
        return any(pattern.search(lowered) for pattern in TEMPORAL_AMBIGUITY_PATTERNS)

    def _looks_like_destructive_path_operation(self, lowered: str) -> bool:
        if not any(pattern.search(lowered) for pattern in DESTRUCTIVE_ACTION_PATTERNS):
            return False
        return any(
            token in lowered
            for token in ("/", "\\", ".git", ".env", "system32", "root", "repo", "folder", "directory", "files")
        )

    def _has_required_context(self, key: str, context: dict[str, Any], policy: PolicyContext) -> bool:
        if key == "path_privilege":
            return policy.path_privilege is not None
        return bool(context.get(key))
