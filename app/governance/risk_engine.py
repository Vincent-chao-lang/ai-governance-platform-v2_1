from __future__ import annotations
from typing import Dict, Tuple

SEVERITY_SCORE = {"low": 10, "med": 30, "high": 70}

def score_risks(risk_flags: Dict[str, dict]) -> Tuple[int, str]:
    if not risk_flags:
        return 0, "none"
    score = 0
    worst = "low"
    for _, meta in risk_flags.items():
        sev = meta.get("severity", "low")
        score = max(score, SEVERITY_SCORE.get(sev, 10))
        if SEVERITY_SCORE.get(sev, 10) > SEVERITY_SCORE.get(worst, 10):
            worst = sev
    return score, worst
