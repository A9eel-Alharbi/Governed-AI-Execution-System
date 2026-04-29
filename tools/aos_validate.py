#!/usr/bin/env python3
"""Minimal AOS/CDD v2 validation CLI.

This tool intentionally avoids external dependencies beyond PyYAML, which is
commonly present in Python environments used for CI. It validates the
framework's machine-readable artifacts against the repository's own schemas and
can emit a machine-readable vault health report.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MACHINE_DIR = ROOT / "machine"


ARTIFACT_SCHEMAS = {
    "context-loader.schema.json": [
        "_templates/ops/session-loader.yaml",
        "examples/*/sessions/session-*.yaml",
    ],
    "vault-health.schema.json": [
        "_templates/ops/vault-health.yaml",
        "examples/*/ops/vault-health*.yaml",
    ],
    "command-registry.schema.json": [
        "_templates/ops/command-registry.yaml",
        "examples/*/ops/command-registry.yaml",
    ],
    "policy-profile.schema.json": [
        "_templates/ops/policy-profile.yaml",
        "examples/*/ops/policy-profile.yaml",
    ],
    "approval-record.schema.json": [
        "_templates/ops/approval-record.yaml",
        "examples/*/ops/APR-*.yaml",
    ],
    "ccr.schema.json": [
        "_templates/work-packages/constraint-change-request.yaml",
        "examples/*/ops/CCR-*.yaml",
    ],
    "completion-report.schema.json": [
        "examples/*/sessions/completion-report-*.yaml",
    ],
    "impact-assessment.schema.json": [
        "_templates/ops/impact-assessment.yaml",
        "examples/*/ops/impact-assessment-*.yaml",
    ],
    "blocker-report.schema.json": [
        "_templates/ops/blocker-report.yaml",
        "examples/*/sessions/blocker-report-*.yaml",
    ],
    "conflict-report.schema.json": [
        "_templates/ops/conflict-report.yaml",
        "examples/*/sessions/conflict-report-*.yaml",
    ],
}


@dataclass
class ValidationErrorDetail:
    path: str
    message: str


@dataclass
class SessionConstraint:
    document: str
    permission: str


def load_text_data(path: Path) -> Any:
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix in {".yaml", ".yml"}:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    raise ValueError(f"Unsupported file type: {path}")


def is_type(value: Any, schema_type: str) -> bool:
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if schema_type == "boolean":
        return isinstance(value, bool)
    return True


def validate_format(value: str, fmt: str) -> bool:
    if fmt == "date":
        try:
            date.fromisoformat(value)
            return True
        except ValueError:
            return False
    if fmt == "date-time":
        normalized = value.replace("Z", "+00:00")
        try:
            datetime.fromisoformat(normalized)
            return True
        except ValueError:
            return False
    return True


def validate_against_schema(value: Any, schema: dict[str, Any], path: str = "$") -> list[ValidationErrorDetail]:
    errors: list[ValidationErrorDetail] = []

    schema_type = schema.get("type")
    if schema_type and not is_type(value, schema_type):
        return [ValidationErrorDetail(path, f"Expected {schema_type}, got {type(value).__name__}")]

    if "enum" in schema and value not in schema["enum"]:
        errors.append(ValidationErrorDetail(path, f"Value {value!r} not in enum {schema['enum']!r}"))

    if isinstance(value, (int, float)) and "minimum" in schema and value < schema["minimum"]:
        errors.append(ValidationErrorDetail(path, f"Value {value} below minimum {schema['minimum']}"))

    if isinstance(value, str) and "format" in schema and not validate_format(value, schema["format"]):
        errors.append(ValidationErrorDetail(path, f"Value {value!r} does not match format {schema['format']}"))

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(ValidationErrorDetail(path, f"Missing required property {key!r}"))

        properties = schema.get("properties", {})
        for key, child in value.items():
            if key in properties:
                errors.extend(validate_against_schema(child, properties[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(ValidationErrorDetail(path, f"Unexpected property {key!r}"))

    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            errors.extend(validate_against_schema(item, schema["items"], f"{path}[{index}]"))

    return errors


def iter_artifact_targets(root: Path) -> list[tuple[Path, Path]]:
    results: list[tuple[Path, Path]] = []
    for schema_name, patterns in ARTIFACT_SCHEMAS.items():
        schema_path = MACHINE_DIR / schema_name
        for pattern in patterns:
            for file_path in root.glob(pattern):
                if file_path.is_file():
                    results.append((file_path, schema_path))
    return sorted(results, key=lambda item: str(item[0]))


def find_wp_file(root: Path, wp_id: str) -> Path | None:
    for candidate in root.glob(f"**/{wp_id}*.md"):
        if "work-packages" in candidate.parts:
            return candidate
    return None


def extract_wp_constraints(wp_path: Path) -> list[SessionConstraint]:
    lines = wp_path.read_text(encoding="utf-8").splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == "## 5. Constraint Documents To Load":
            start = index + 1
            break
    if start is None:
        return []

    constraints: list[SessionConstraint] = []
    table_rows: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if stripped.startswith("|"):
            table_rows.append(stripped)
    for row in table_rows[2:]:
        cells = [cell.strip().strip("`") for cell in row.strip("|").split("|")]
        if len(cells) >= 3:
            constraints.append(SessionConstraint(document=cells[0], permission=cells[2]))
    return constraints


def compare_session_to_wp(root: Path, session_path: Path, session_data: dict[str, Any]) -> list[ValidationErrorDetail]:
    if "_templates" in session_path.parts:
        return []
    wp_id = session_data.get("work_package_id")
    if not isinstance(wp_id, str):
        return [ValidationErrorDetail("$", "Session loader missing work_package_id for WP consistency check")]
    wp_path = find_wp_file(root, wp_id)
    if wp_path is None:
        return [ValidationErrorDetail("$", f"No work package file found for {wp_id!r}")]

    wp_constraints = extract_wp_constraints(wp_path)
    session_constraints = [
        SessionConstraint(document=item["document"], permission=item["permission"])
        for item in session_data.get("constraints_to_load", [])
        if isinstance(item, dict)
    ]

    errors: list[ValidationErrorDetail] = []
    for wp_constraint in wp_constraints:
        matched = next(
            (
                session_constraint
                for session_constraint in session_constraints
                if session_constraint.document.endswith(wp_constraint.document)
            ),
            None,
        )
        if matched is None:
            errors.append(
                ValidationErrorDetail(
                    "$.constraints_to_load",
                    f"Session loader is missing WP-declared constraint {wp_constraint.document!r}",
                )
            )
            continue
        if matched.permission != wp_constraint.permission:
            errors.append(
                ValidationErrorDetail(
                    "$.constraints_to_load",
                    f"Permission mismatch for {wp_constraint.document!r}: session={matched.permission!r}, wp={wp_constraint.permission!r}",
                )
            )
    return errors


def compare_session_policy_profile(root: Path, session_path: Path, session_data: dict[str, Any]) -> list[ValidationErrorDetail]:
    if "_templates" in session_path.parts:
        return []
    policy_profile = session_data.get("policy_profile")
    if not isinstance(policy_profile, dict):
        return [ValidationErrorDetail("$.policy_profile", "Session loader missing policy_profile object")]

    document = policy_profile.get("document")
    if not isinstance(document, str) or not document:
        return [ValidationErrorDetail("$.policy_profile.document", "Session loader policy_profile.document must be a non-empty string")]

    policy_path = root / document
    errors: list[ValidationErrorDetail] = []
    if not policy_path.exists():
        errors.append(
            ValidationErrorDetail(
                "$.policy_profile.document",
                f"Referenced policy profile does not exist: {document!r}",
            )
        )

    vault_health = session_data.get("vault_health")
    checked_from = vault_health.get("checked_from") if isinstance(vault_health, dict) else None
    if not isinstance(checked_from, str) or not checked_from:
        errors.append(
            ValidationErrorDetail(
                "$.vault_health.checked_from",
                "Session loader must declare vault_health.checked_from for policy-profile enforcement",
            )
        )
        return errors

    vault_path = root / checked_from
    if not vault_path.exists():
        errors.append(
            ValidationErrorDetail(
                "$.vault_health.checked_from",
                f"Referenced vault health file does not exist: {checked_from!r}",
            )
        )
        return errors

    vault_data = load_text_data(vault_path)
    documents = vault_data.get("documents", []) if isinstance(vault_data, dict) else []
    if not any(isinstance(item, dict) and item.get("path") == document for item in documents):
        errors.append(
            ValidationErrorDetail(
                "$.policy_profile.document",
                f"Policy profile {document!r} is not tracked in {checked_from!r}",
            )
        )
    return errors


def classify_document(path_text: str, document_id: str) -> tuple[int, int]:
    key = f"{document_id} {path_text}".lower()
    if "schema" in key or "openapi" in key or "api" in key:
        return (7, 14)
    if "vision" in key:
        return (30, 60)
    if "security" in key or "testing" in key:
        return (30, 45)
    return (14, 30)


def days_since(last_validated: str) -> int:
    validated = date.fromisoformat(last_validated)
    today = datetime.now(timezone.utc).date()
    return (today - validated).days


def compute_flag(document_id: str, path_text: str, last_validated: str) -> str:
    green_days, yellow_days = classify_document(path_text, document_id)
    elapsed = days_since(last_validated)
    if elapsed <= green_days:
        return "green"
    if elapsed <= yellow_days:
        return "yellow"
    return "red"


def build_health_report(root: Path) -> dict[str, Any]:
    dashboards = []
    for dashboard_path in sorted(root.glob("**/vault-health.yaml")):
        if "_templates" in dashboard_path.parts:
            continue
        data = load_text_data(dashboard_path)
        documents_report = []
        cross_document_checks = data.get("cross_document_checks", [])
        for document in data.get("documents", []):
            path_text = document["path"]
            absolute_target = root / path_text
            computed_flag = compute_flag(document["id"], path_text, document["last_validated"])
            documents_report.append(
                {
                    "id": document["id"],
                    "path": path_text,
                    "exists": absolute_target.exists(),
                    "computed_staleness_flag": computed_flag,
                    "declared_staleness_flag": document.get("staleness_flag"),
                    "last_validated": document["last_validated"],
                    "validation_method": document.get("validation_method"),
                }
            )
        dashboards.append(
            {
                "dashboard": str(dashboard_path.relative_to(root)),
                "documents": documents_report,
                "open_constraint_conflicts": data.get("open_constraint_conflicts", []),
                "ccrs_in_flight": data.get("ccrs_in_flight", []),
                "cross_document_checks": cross_document_checks,
            }
        )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dashboards": dashboards,
    }


def cmd_validate(args: argparse.Namespace) -> int:
    errors_found = False
    for file_path, schema_path in iter_artifact_targets(args.root):
        data = load_text_data(file_path)
        schema = load_text_data(schema_path)
        errors = validate_against_schema(data, schema)
        if schema_path.name == "context-loader.schema.json" and isinstance(data, dict):
            errors.extend(compare_session_to_wp(args.root, file_path, data))
            errors.extend(compare_session_policy_profile(args.root, file_path, data))
        if errors:
            errors_found = True
            print(f"[FAIL] {file_path.relative_to(args.root)} against {schema_path.name}")
            for err in errors:
                print(f"  - {err.path}: {err.message}")
        else:
            print(f"[PASS] {file_path.relative_to(args.root)}")
    return 1 if errors_found else 0


def cmd_health(args: argparse.Namespace) -> int:
    report = build_health_report(args.root)
    output_path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {output_path.relative_to(args.root)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AOS/CDD v2 repository artifacts.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate machine-readable artifacts against schemas")
    validate_parser.set_defaults(func=cmd_validate)

    health_parser = subparsers.add_parser("health-report", help="Generate a machine-readable vault health report")
    health_parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports" / "vault-health-report.json",
        help="Output path for the generated JSON report",
    )
    health_parser.set_defaults(func=cmd_health)

    args = parser.parse_args()
    args.root = args.root.resolve()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
