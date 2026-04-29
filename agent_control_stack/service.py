from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .executor import ExecutionError, GovernedExecutor
from .models import DecisionEnvelope, DecisionEvent, DispatchTarget
from .pipeline import AgentControlPipeline
from .schema_validation import SchemaValidationError, load_schema, validate_payload
from .store import FileSystemRunStore


DEFAULT_REGISTRY = Path("agent_control_stack") / "runtime" / "case_registry.yaml"
DEFAULT_STORE = Path("runs")
SCHEMA_DIR = Path("agent_control_stack") / "schemas"
MAX_REQUEST_BYTES = 64 * 1024
MAX_TEXT_LENGTH = 4_000


@dataclass
class ServiceRuntime:
    pipeline: AgentControlPipeline
    executor: GovernedExecutor
    store: FileSystemRunStore
    interpret_request_schema: dict[str, Any]
    execute_request_schema: dict[str, Any]
    decision_schema: dict[str, Any]
    execution_schema: dict[str, Any]
    policy_schema: dict[str, Any]


def create_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    registry: str | Path = DEFAULT_REGISTRY,
    store_dir: str | Path = DEFAULT_STORE,
) -> ThreadingHTTPServer:
    runtime = ServiceRuntime(
        pipeline=AgentControlPipeline.from_registry_file(registry),
        executor=GovernedExecutor(),
        store=FileSystemRunStore(store_dir),
        interpret_request_schema=load_schema(SCHEMA_DIR / "interpret-request.schema.json"),
        execute_request_schema=load_schema(SCHEMA_DIR / "execute-request.schema.json"),
        decision_schema=load_schema(SCHEMA_DIR / "decision-envelope.schema.json"),
        execution_schema=load_schema(SCHEMA_DIR / "execution-result.schema.json"),
        policy_schema=load_schema(SCHEMA_DIR / "policy.schema.json"),
    )

    class RequestHandler(BaseHTTPRequestHandler):
        server_version = "AgentControlStackHTTP/0.1"

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                self._write_json(HTTPStatus.OK, {"status": "ok"})
                return
            if parsed.path == "/runs":
                self._write_json(HTTPStatus.OK, {"runs": runtime.store.list_runs()})
                return
            if parsed.path.startswith("/runs/"):
                run_id = parsed.path.removeprefix("/runs/").strip()
                if not run_id:
                    self._write_json(HTTPStatus.BAD_REQUEST, {"error": "missing_run_id"})
                    return
                try:
                    payload = runtime.store.load_run(run_id)
                except FileNotFoundError:
                    self._write_json(HTTPStatus.NOT_FOUND, {"error": "run_not_found"})
                    return
                self._write_json(HTTPStatus.OK, payload)
                return
            self._write_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            try:
                body = self._read_json_body()
            except UnsupportedMediaTypeError as exc:
                self._write_json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "unsupported_media_type", "detail": str(exc)})
                return
            except RequestTooLargeError as exc:
                self._write_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "request_too_large", "detail": str(exc)})
                return
            except ValueError as exc:
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json", "detail": str(exc)})
                return

            if parsed.path == "/interpret":
                self._handle_interpret(body)
                return
            if parsed.path == "/execute":
                self._handle_execute(body)
                return
            self._write_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

        def log_message(self, format: str, *args: object) -> None:
            return

        def _handle_interpret(self, body: dict[str, Any]) -> None:
            try:
                validate_payload(body, runtime.interpret_request_schema)
            except SchemaValidationError as exc:
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_request", "detail": str(exc)})
                return
            text = body.get("text")
            if not isinstance(text, str) or not text.strip():
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "missing_text"})
                return
            if len(text) > MAX_TEXT_LENGTH:
                self._write_json(
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    {"error": "text_too_large", "detail": f"text exceeds {MAX_TEXT_LENGTH} characters"},
                )
                return

            context = _normalize_context(body.get("context"))
            policy_payload = context.get("policy")
            if policy_payload is not None:
                try:
                    validate_payload(policy_payload, runtime.policy_schema)
                except SchemaValidationError as exc:
                    self._write_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_policy", "detail": str(exc)})
                    return
            envelope = runtime.pipeline.decide(text, context)
            payload: dict[str, Any] = {"decision": envelope.to_dict()}

            execution = None
            if body.get("execute") is True and envelope.outcome == "dispatch":
                try:
                    execution = runtime.executor.execute(envelope, context)
                except ExecutionError as exc:
                    self._write_json(
                        HTTPStatus.CONFLICT,
                        {"error": "execution_failed", "detail": str(exc), "decision": envelope.to_dict()},
                    )
                    return
                payload["execution"] = execution.to_dict()
                validate_payload(payload["execution"], runtime.execution_schema)

            if body.get("persist") is True:
                record = runtime.store.persist(envelope, execution, context)
                payload["persistence"] = {
                    "run_id": record.run_id,
                    "decision_path": record.decision_path,
                    "execution_path": record.execution_path,
                }

            status = HTTPStatus.OK
            if envelope.outcome == "clarify":
                status = HTTPStatus.UNPROCESSABLE_ENTITY
            elif envelope.outcome == "refuse":
                status = HTTPStatus.FORBIDDEN
            elif envelope.outcome == "escalate":
                status = HTTPStatus.CONFLICT
            validate_payload(payload["decision"], runtime.decision_schema)
            self._write_json(status, payload)

        def _handle_execute(self, body: dict[str, Any]) -> None:
            try:
                validate_payload(body, runtime.execute_request_schema)
            except SchemaValidationError as exc:
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_request", "detail": str(exc)})
                return
            decision_payload = body.get("decision")
            if not isinstance(decision_payload, dict):
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "missing_decision"})
                return
            try:
                validate_payload(decision_payload, runtime.decision_schema)
                envelope = _decision_from_dict(decision_payload)
            except (SchemaValidationError, ValueError) as exc:
                self._write_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_decision", "detail": str(exc)})
                return
            context = _normalize_context(body.get("context"))
            policy_payload = context.get("policy")
            if policy_payload is not None:
                try:
                    validate_payload(policy_payload, runtime.policy_schema)
                except SchemaValidationError as exc:
                    self._write_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_policy", "detail": str(exc)})
                    return
            try:
                execution = runtime.executor.execute(envelope, context)
            except ExecutionError as exc:
                self._write_json(HTTPStatus.CONFLICT, {"error": "execution_failed", "detail": str(exc)})
                return
            payload: dict[str, Any] = {"decision": envelope.to_dict(), "execution": execution.to_dict()}
            validate_payload(payload["decision"], runtime.decision_schema)
            validate_payload(payload["execution"], runtime.execution_schema)
            if body.get("persist") is True:
                record = runtime.store.persist(envelope, execution, context)
                payload["persistence"] = {
                    "run_id": record.run_id,
                    "decision_path": record.decision_path,
                    "execution_path": record.execution_path,
                }
            self._write_json(HTTPStatus.OK, payload)

        def _read_json_body(self) -> dict[str, Any]:
            content_type = self.headers.get("Content-Type", "")
            media_type = content_type.split(";", 1)[0].strip().lower()
            if media_type not in {"application/json", "text/json"}:
                raise UnsupportedMediaTypeError("Content-Type must be application/json.")
            length_text = self.headers.get("Content-Length", "0")
            try:
                length = int(length_text)
            except ValueError as exc:
                raise ValueError("Invalid Content-Length.") from exc
            if length < 0:
                raise ValueError("Content-Length must not be negative.")
            if length > MAX_REQUEST_BYTES:
                raise RequestTooLargeError(f"Request body exceeds {MAX_REQUEST_BYTES} bytes.")
            raw = self.rfile.read(length) if length > 0 else b"{}"
            parsed = json.loads(raw.decode("utf-8"))
            if not isinstance(parsed, dict):
                raise ValueError("JSON body must be an object.")
            return parsed

        def _write_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            data = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return ThreadingHTTPServer((host, port), RequestHandler)


def _normalize_context(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    context = dict(value)
    if "today" in context and isinstance(context["today"], str):
        context["today"] = date.fromisoformat(context["today"])
    return context


def _decision_from_dict(data: dict[str, Any]) -> DecisionEnvelope:
    dispatch_payload = data.get("dispatch_target")
    dispatch_target = None
    if dispatch_payload is not None:
        if not isinstance(dispatch_payload, dict):
            raise ValueError("dispatch_target must be an object.")
        dispatch_target = DispatchTarget(
            case_id=str(dispatch_payload["case_id"]),
            procedure=str(dispatch_payload["procedure"]),
            target=str(dispatch_payload["target"]),
            human_review_gate=bool(dispatch_payload.get("human_review_gate", False)),
        )

    return DecisionEnvelope(
        raw_input=str(data["raw_input"]),
        restored_input=str(data["restored_input"]),
        normalized_input=str(data["normalized_input"]),
        outcome=str(data["outcome"]),
        case_id=data.get("case_id"),
        rationale=str(data.get("rationale", "")),
        clarification_question=data.get("clarification_question"),
        refusal_reason=data.get("refusal_reason"),
        escalation_reason=data.get("escalation_reason"),
        decision_trace=[
            DecisionEvent(stage=str(item["stage"]), detail=str(item["detail"]))
            for item in data.get("decision_trace", [])
            if isinstance(item, dict)
        ],
        dispatch_target=dispatch_target,
    )


class RequestTooLargeError(ValueError):
    """Raised when the HTTP request body exceeds the service limit."""


class UnsupportedMediaTypeError(ValueError):
    """Raised when the HTTP request body content type is unsupported."""


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the agent control stack HTTP service.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--store-dir", type=Path, default=DEFAULT_STORE)
    args = parser.parse_args()

    server = create_server(args.host, args.port, args.registry, args.store_dir)
    try:
        print(f"Serving on http://{args.host}:{args.port}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
