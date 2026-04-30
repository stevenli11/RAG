"""In-memory registry for skills."""

from __future__ import annotations

from typing import Any, Dict

from .base import Skill, SkillContext


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill

    def run(self, name: str, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        if name not in self._skills:
            raise KeyError(f"Skill not found: {name}")
        return self._skills[name].run(ctx, **kwargs)

    def list_names(self) -> list[str]:
        return sorted(self._skills.keys())
