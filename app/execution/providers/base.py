from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Tuple, Protocol, List

@dataclass
class ProviderSpec:
    name: str
    kind: str  # mock | openai_compat | openai
    base_url_env: str | None = None
    api_key_env: str | None = None
    timeout_s: int = 30

class Provider(Protocol):
    async def chat(self, *, model: str, messages: List[Dict[str, Any]], temperature: float, max_tokens: int) -> Tuple[str, Dict[str, int]]:
        ...
