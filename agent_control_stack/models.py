from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


ALLOWED_OUTCOMES = {"clarify", "refuse", "dispatch", "escalate"}


@dataclass(frozen=True)
class RestorationEvent:
    source: str
    replacement: str
    reason: str


@dataclass(frozen=True)
class BalancingEvent:
    kind: str
    detail: str


@dataclass(frozen=True)
class DecisionEvent:
    stage: str
    detail: str


@dataclass(frozen=True)
class DispatchTarget:
    case_id: str
    procedure: str
    target: str
    human_review_gate: bool


@dataclass
class DecisionEnvelope:
    raw_input: str
    restored_input: str
    normalized_input: str
    outcome: str
    case_id: str | None = None
    rationale: str = ""
    clarification_question: str | None = None
    refusal_reason: str | None = None
    escalation_reason: str | None = None
    restoration_trace: list[RestorationEvent] = field(default_factory=list)
    balancing_trace: list[BalancingEvent] = field(default_factory=list)
    decision_trace: list[DecisionEvent] = field(default_factory=list)
    dispatch_target: DispatchTarget | None = None

    def __post_init__(self) -> None:
        if self.outcome not in ALLOWED_OUTCOMES:
            raise ValueError(f"Unsupported outcome: {self.outcome}")

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["restoration_trace"] = [asdict(item) for item in self.restoration_trace]
        result["balancing_trace"] = [asdict(item) for item in self.balancing_trace]
        result["decision_trace"] = [asdict(item) for item in self.decision_trace]
        if self.dispatch_target is not None:
            result["dispatch_target"] = asdict(self.dispatch_target)
        return {key: value for key, value in result.items() if value is not None}
