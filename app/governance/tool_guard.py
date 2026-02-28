from __future__ import annotations
from typing import Dict, Any, Tuple, Optional, Literal
ActionType = Literal["READ", "WRITE"]

def check_tool_allowed(policy: Dict[str, Any], *, tool_name: str, action_type: ActionType) -> Tuple[bool, Optional[str]]:
    tools = policy.get("tools") or {}
    if not tools.get("enabled", False):
        return False, "tools disabled by policy"
    allowlist = set(tools.get("allowlist") or [])
    if allowlist and tool_name not in allowlist:
        return False, "tool not in allowlist"
    if action_type == "WRITE":
        write_tools = set(tools.get("write_tools") or [])
        if write_tools and tool_name not in write_tools:
            return False, "WRITE not allowed for this tool"
    return True, None
