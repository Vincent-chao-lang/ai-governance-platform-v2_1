from __future__ import annotations
import yaml, os
from typing import Any, Dict

POLICY_PATH = os.getenv("POLICY_PATH", "config/policy.yaml")

class PolicyEngine:
    def __init__(self, policy_path: str = POLICY_PATH):
        self.policy_path = policy_path
        self._policy: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        with open(self.policy_path, "r", encoding="utf-8") as f:
            self._policy = yaml.safe_load(f) or {}

    @property
    def version(self) -> str:
        return str(self._policy.get("version", "unknown"))

    def resolve(self, department: str) -> Dict[str, Any]:
        default = self._policy.get("default", {})
        dep = (self._policy.get("departments", {}) or {}).get(department, {})
        merged = dict(default)
        for k, v in dep.items():
            if isinstance(v, dict) and isinstance(merged.get(k), dict):
                merged[k] = {**merged[k], **v}
            else:
                merged[k] = v
        return merged
