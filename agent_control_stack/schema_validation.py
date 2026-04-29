from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SchemaValidationError(ValueError):
    """Raised when a payload does not conform to the expected schema."""


def load_schema(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_payload(payload: Any, schema: dict[str, Any], path: str = "$") -> None:
    schema_type = schema.get("type")
    if schema_type is not None and not _is_type(payload, schema_type):
        raise SchemaValidationError(f"{path}: expected {schema_type}, got {type(payload).__name__}")

    if "enum" in schema and payload not in schema["enum"]:
        raise SchemaValidationError(f"{path}: value {payload!r} not in enum {schema['enum']!r}")

    if isinstance(payload, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in payload:
                raise SchemaValidationError(f"{path}: missing required property {key!r}")
        if schema.get("additionalProperties") is False:
            for key in payload:
                if key not in properties:
                    raise SchemaValidationError(f"{path}: unexpected property {key!r}")
        for key, value in payload.items():
            if key in properties:
                validate_payload(value, properties[key], f"{path}.{key}")
        return

    if isinstance(payload, list):
        items_schema = schema.get("items")
        if items_schema is None:
            return
        for index, item in enumerate(payload):
            validate_payload(item, items_schema, f"{path}[{index}]")


def _is_type(value: Any, schema_type: str) -> bool:
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "boolean":
        return isinstance(value, bool)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if schema_type == "null":
        return value is None
    return True
