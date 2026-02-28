from __future__ import annotations
import os
import httpx
from typing import Any, Dict, Tuple, List

class OpenAICompatProvider:
    """Calls an OpenAI-compatible endpoint using /chat/completions."""
    def __init__(self, *, base_url: str, api_key: str = "", timeout_s: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout_s

    async def chat(self, *, model: str, messages: List[Dict[str, Any]], temperature: float, max_tokens: int) -> Tuple[str, Dict[str, int]]:
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()

        # Parse standard OpenAI response format
        reply = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {}) or {}
        usage = {
            "prompt_tokens": int(usage.get("prompt_tokens", 0)),
            "completion_tokens": int(usage.get("completion_tokens", 0)),
            "total_tokens": int(usage.get("total_tokens", 0)),
        }
        return reply, usage
