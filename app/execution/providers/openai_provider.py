from __future__ import annotations
from .openai_compat_provider import OpenAICompatProvider

class OpenAIProvider(OpenAICompatProvider):
    """Same implementation as OpenAI-compatible provider; base_url should be https://api.openai.com/v1"""
    pass
