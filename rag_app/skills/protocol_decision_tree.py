"""Decision-tree skill for protocol path and risk notes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from .base import SkillContext


class ProtocolDecisionTreeSkill:
    name = "protocol_decision_tree"

    def __init__(self, tree_path: str | None = None) -> None:
        default_path = Path(__file__).with_name("protocol_tree.yaml")
        self.tree_path = Path(tree_path) if tree_path else default_path
        self.tree = yaml.safe_load(self.tree_path.read_text(encoding="utf-8"))

    def run(self, ctx: SkillContext, **kwargs: Any) -> Dict[str, Any]:
        question = str(kwargs.get("question") or "").lower()
        for route in self.tree.get("routes", []):
            keys = [k.lower() for k in route.get("match_any", [])]
            if any(k in question for k in keys):
                return {
                    "route_id": route.get("id"),
                    "protocol_path": route.get("protocol_path"),
                    "risk_flags": route.get("risk_flags", []),
                    "required_checks": route.get("required_checks", []),
                }
        default = self.tree.get("default", {})
        return {
            "route_id": "default",
            "protocol_path": default.get("protocol_path", "General"),
            "risk_flags": default.get("risk_flags", []),
            "required_checks": default.get("required_checks", []),
        }
