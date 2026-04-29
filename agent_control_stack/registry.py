from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RegisteredCase:
    case_id: str
    procedure: str
    target: str
    human_review_gate: bool
    required_context: tuple[str, ...]


class CaseRegistry:
    def __init__(self, cases: dict[str, RegisteredCase]) -> None:
        self._cases = cases

    @classmethod
    def from_yaml(cls, path: Path) -> "CaseRegistry":
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cases: dict[str, RegisteredCase] = {}
        for item in data.get("cases", []):
            case = RegisteredCase(
                case_id=item["case_id"],
                procedure=item["procedure"],
                target=item["target"],
                human_review_gate=bool(item.get("human_review_gate", False)),
                required_context=tuple(item.get("required_context", [])),
            )
            cases[case.case_id] = case
        return cls(cases)

    def get(self, case_id: str) -> RegisteredCase | None:
        return self._cases.get(case_id)

    def require_known_case(self, case_id: str) -> RegisteredCase:
        case = self.get(case_id)
        if case is None:
            raise KeyError(case_id)
        return case

    @property
    def case_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._cases))
