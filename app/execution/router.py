from __future__ import annotations
import os
from typing import Dict, Any, Tuple, List

from .providers.base import ProviderSpec
from .providers.mock_provider import MockProvider
from .providers.openai_compat_provider import OpenAICompatProvider
from .providers.openai_provider import OpenAIProvider

class ModelRouter:
    """Execution Engine router with provider abstraction + fallback.
    Governance decides provider order via policy.yaml.
    """

    def _build_provider(self, spec: ProviderSpec):
        kind = spec.kind
        if kind == "mock":
            return MockProvider()
        if kind == "openai_compat":
            base_url = os.getenv(spec.base_url_env or "", "").strip()
            if not base_url:
                raise ValueError(f"Missing base_url env for provider {spec.name} (env={spec.base_url_env})")
            api_key = os.getenv(spec.api_key_env or "", "").strip()
            return OpenAICompatProvider(base_url=base_url, api_key=api_key, timeout_s=spec.timeout_s)
        if kind == "openai":
            base_url = os.getenv(spec.base_url_env or "OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
            api_key = os.getenv(spec.api_key_env or "OPENAI_API_KEY", "").strip()
            if not api_key:
                raise ValueError("Missing OPENAI_API_KEY for openai provider")
            return OpenAIProvider(base_url=base_url, api_key=api_key, timeout_s=spec.timeout_s)
        raise ValueError(f"Unknown provider kind: {kind}")

    async def run(
        self,
        *,
        providers: List[Dict[str, Any]],
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, Dict[str, int], str]:
        """Returns (reply, usage, provider_name)."""
        last_err: Exception | None = None

        for p in providers:
            spec = ProviderSpec(
                name=str(p.get("name", "provider")),
                kind=str(p.get("kind", "mock")),
                base_url_env=p.get("base_url_env"),
                api_key_env=p.get("api_key_env"),
                timeout_s=int(p.get("timeout_s", 30)),
            )
            try:
                provider = self._build_provider(spec)
                reply, usage = await provider.chat(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
                return reply, usage, spec.name
            except Exception as e:
                last_err = e
                continue

        raise RuntimeError(f"All providers failed. Last error: {last_err}")
