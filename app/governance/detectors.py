from __future__ import annotations
import re
from typing import Dict, List, Tuple

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SECRET_RE = re.compile(r"(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----)")
INJECTION_HINTS = [
    "ignore previous instructions",
    "system prompt",
    "reveal",
    "exfiltrate",
    "bypass",
    "developer message",
]

def detect_pii(text: str) -> Tuple[bool, List[str]]:
    hits = EMAIL_RE.findall(text)
    return (len(hits) > 0), hits

def detect_secrets(text: str) -> Tuple[bool, List[str]]:
    hits = SECRET_RE.findall(text)
    return (len(hits) > 0), [h[:10] + "..." for h in hits]

def detect_prompt_injection(text: str) -> Tuple[bool, List[str]]:
    lowered = text.lower()
    hits = [h for h in INJECTION_HINTS if h in lowered]
    return (len(hits) > 0), hits

def run_detectors(text: str, enabled: Dict[str, bool]) -> Dict[str, dict]:
    results: Dict[str, dict] = {}
    if enabled.get("pii", True):
        ok, hits = detect_pii(text)
        if ok:
            results["pii"] = {"severity": "med", "hits": hits}
    if enabled.get("secrets", True):
        ok, hits = detect_secrets(text)
        if ok:
            results["secrets"] = {"severity": "high", "hits": hits}
    if enabled.get("prompt_injection", True):
        ok, hits = detect_prompt_injection(text)
        if ok:
            results["prompt_injection"] = {"severity": "med", "hits": hits}
    return results
