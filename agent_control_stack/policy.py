from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .schema_validation import SchemaValidationError, load_schema, validate_payload


SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"
POLICY_SCHEMA_PATH = SCHEMA_DIR / "policy.schema.json"
POLICY_PROFILE_SCHEMA_PATH = SCHEMA_DIR / "policy-profile.schema.json"
APPROVAL_RECORD_SCHEMA_PATH = SCHEMA_DIR / "approval-record.schema.json"


class PolicyResolutionError(ValueError):
    """Raised when policy data cannot be resolved safely."""


@dataclass(frozen=True)
class PolicyContext:
    environment: str = "dev"
    approval_state: str = "unapproved"
    target_class: str = "general"
    destructive_action: bool = False
    path_privilege: str | None = None

    @classmethod
    def from_context(cls, context: dict[str, Any]) -> "PolicyContext":
        policy = context.get("policy")
        if isinstance(policy, dict):
            return cls.from_mapping(policy)
        return cls.from_mapping(context)

    @classmethod
    def from_mapping(cls, mapping: dict[str, Any]) -> "PolicyContext":
        return cls(
            environment=str(mapping.get("environment", "dev")),
            approval_state=str(mapping.get("approval_state", "unapproved")),
            target_class=str(mapping.get("target_class", "general")),
            destructive_action=bool(mapping.get("destructive_action", False)),
            path_privilege=_optional_string(mapping.get("path_privilege")),
        )

    def requires_escalation(self) -> bool:
        return self.target_class in {"security", "production", "infrastructure"} and self.approval_state != "approved"

    def allows_protected_change(self) -> bool:
        return self.path_privilege is not None or self.approval_state == "approved"


@dataclass(frozen=True)
class PolicyProfile:
    defaults: dict[str, Any]
    case_overrides: dict[str, dict[str, Any]]
    source_path: Path | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any], source_path: Path | None = None) -> "PolicyProfile":
        return cls(
            defaults=dict(payload.get("defaults", {})),
            case_overrides={
                str(case_id): dict(case_payload)
                for case_id, case_payload in payload.get("case_overrides", {}).items()
                if isinstance(case_payload, dict)
            },
            source_path=source_path,
        )

    def resolve(self, case_id: str | None = None) -> dict[str, Any]:
        resolved = dict(self.defaults)
        if case_id is not None:
            resolved.update(self.case_overrides.get(case_id, {}))
        return resolved


@dataclass(frozen=True)
class ApprovalRecord:
    status: str
    case_ids: tuple[str, ...]
    target_classes: tuple[str, ...]
    environments: tuple[str, ...]
    policy_overlay: dict[str, Any]
    source_path: Path | None = None

    @classmethod
    def from_payload(cls, payload: dict[str, Any], source_path: Path | None = None) -> "ApprovalRecord":
        scope = payload.get("scope", {})
        return cls(
            status=str(payload.get("status", "draft")),
            case_ids=tuple(str(item) for item in scope.get("case_ids", [])),
            target_classes=tuple(str(item) for item in scope.get("target_classes", [])),
            environments=tuple(str(item) for item in scope.get("environments", [])),
            policy_overlay=dict(payload.get("policy_overlay", {})),
            source_path=source_path,
        )

    def applies_to(self, case_id: str | None, merged_policy: dict[str, Any]) -> bool:
        if self.status != "approved":
            return False
        if case_id is not None and self.case_ids and case_id not in self.case_ids:
            return False
        target_class = str(merged_policy.get("target_class", "general"))
        environment = str(merged_policy.get("environment", "dev"))
        if self.target_classes and target_class not in self.target_classes:
            return False
        if self.environments and environment not in self.environments:
            return False
        return True


def resolve_policy_context(context: dict[str, Any], case_id: str | None = None) -> PolicyContext:
    profile = load_policy_profile_from_context(context)
    merged: dict[str, Any] = {}
    if profile is not None:
        merged.update(profile.resolve(case_id))

    approval = load_approval_record_from_context(context)
    if approval is not None and approval.applies_to(case_id, merged):
        merged.update(approval.policy_overlay)

    policy = context.get("policy")
    if isinstance(policy, dict):
        _validate_policy_mapping(policy, source="context.policy")
        merged.update(policy)
    else:
        legacy = {
            key: context[key]
            for key in ("environment", "approval_state", "target_class", "destructive_action", "path_privilege")
            if key in context
        }
        if legacy:
            _validate_policy_mapping(legacy, source="context")
            merged.update(legacy)

    return PolicyContext.from_mapping(merged)


def load_policy_profile_from_context(context: dict[str, Any]) -> PolicyProfile | None:
    policy_artifact = context.get("policy_artifact")
    if not policy_artifact:
        return None
    return load_policy_profile(_resolve_policy_artifact_path(context, str(policy_artifact)))


def load_policy_profile(path: str | Path) -> PolicyProfile:
    policy_path = Path(path)
    if not policy_path.exists():
        raise PolicyResolutionError(f"Policy artifact not found: {policy_path}")
    payload = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise PolicyResolutionError(f"Policy artifact must be a YAML object: {policy_path}")
    schema = load_schema(POLICY_PROFILE_SCHEMA_PATH)
    try:
        validate_payload(payload, schema)
    except SchemaValidationError as exc:
        raise PolicyResolutionError(f"Invalid policy artifact {policy_path}: {exc}") from exc
    defaults = dict(payload.get("defaults", {}))
    _validate_policy_mapping(defaults, source=f"{policy_path}.defaults")
    for case_id, override in payload.get("case_overrides", {}).items():
        if isinstance(override, dict):
            _validate_policy_mapping(override, source=f"{policy_path}.case_overrides.{case_id}")
    return PolicyProfile.from_payload(payload, policy_path)


def load_approval_record_from_context(context: dict[str, Any]) -> ApprovalRecord | None:
    approval_artifact = context.get("approval_artifact")
    if not approval_artifact:
        return None
    return load_approval_record(_resolve_policy_artifact_path(context, str(approval_artifact)))


def load_approval_record(path: str | Path) -> ApprovalRecord:
    approval_path = Path(path)
    if not approval_path.exists():
        raise PolicyResolutionError(f"Approval artifact not found: {approval_path}")
    payload = yaml.safe_load(approval_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise PolicyResolutionError(f"Approval artifact must be a YAML object: {approval_path}")
    schema = load_schema(APPROVAL_RECORD_SCHEMA_PATH)
    try:
        validate_payload(payload, schema)
    except SchemaValidationError as exc:
        raise PolicyResolutionError(f"Invalid approval artifact {approval_path}: {exc}") from exc
    overlay = dict(payload.get("policy_overlay", {}))
    _validate_policy_mapping(overlay, source=f"{approval_path}.policy_overlay")
    return ApprovalRecord.from_payload(payload, approval_path)


def _resolve_policy_artifact_path(context: dict[str, Any], artifact_path: str) -> Path:
    candidate = Path(artifact_path)
    if candidate.is_absolute():
        return candidate
    repository_root = context.get("repository_root")
    if not repository_root:
        raise PolicyResolutionError("policy_artifact requires repository_root context for relative paths.")
    return Path(str(repository_root)) / candidate


def _validate_policy_mapping(mapping: dict[str, Any], source: str) -> None:
    schema = load_schema(POLICY_SCHEMA_PATH)
    try:
        validate_payload(mapping, schema, path=source)
    except SchemaValidationError as exc:
        raise PolicyResolutionError(str(exc)) from exc


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
