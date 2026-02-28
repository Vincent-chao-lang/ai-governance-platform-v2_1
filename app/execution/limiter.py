from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Dict

@dataclass
class Bucket:
    tokens: float
    last: float

class InMemoryRateLimiter:
    def __init__(self):
        self.buckets: Dict[str, Bucket] = {}

    def allow(self, key: str, rpm: int) -> bool:
        now = time.time()
        rate = rpm / 60.0
        cap = float(rpm)
        b = self.buckets.get(key)
        if b is None:
            b = Bucket(tokens=cap, last=now)
            self.buckets[key] = b
        elapsed = max(0.0, now - b.last)
        b.tokens = min(cap, b.tokens + elapsed * rate)
        b.last = now
        if b.tokens >= 1.0:
            b.tokens -= 1.0
            return True
        return False
