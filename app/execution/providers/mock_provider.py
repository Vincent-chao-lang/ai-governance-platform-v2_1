from __future__ import annotations
from typing import Any, Dict, Tuple, List

class MockProvider:
    async def chat(self, *, model: str, messages: List[Dict[str, Any]], temperature: float, max_tokens: int) -> Tuple[str, Dict[str, int]]:
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "")
                break
        reply = f"[mock:{model}] I received: {last_user}"
        usage = {"prompt_tokens": min(1000, len(str(messages)) // 4), "completion_tokens": min(500, len(reply) // 4)}
        usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]
        return reply, usage
