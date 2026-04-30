"""Skill base types for modular orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Protocol


@dataclass
class SkillContext:
    """Runtime context shared across skills."""

    config: Dict[str, Any]
    state: Dict[str, Any] = field(default_factory=dict)


class Skill(Protocol):
    """Protocol for executable skills."""

    name: str

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        ...
