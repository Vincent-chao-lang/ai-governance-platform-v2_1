from __future__ import annotations
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any
from ..models.db_models import AIRequest, RiskEvent

def _preview(text: str, n: int = 400) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[:n] + "..."

def write_audit(
    db: Session,
    *,
    request_id: str,
    user_id: str,
    department: str,
    model: str,
    route_provider: str,
    policy_version: str,
    risk_score: int,
    risk_flags: Dict[str, Any],
    prompt_text: str,
    response_text: str,
    token_input: int,
    token_output: int,
    latency_ms: int,
    status: str = "ok",
):
    row = AIRequest(
        id=request_id,
        ts=datetime.utcnow(),
        user_id=user_id,
        department=department,
        model=model,
        route_provider=route_provider,
        policy_version=policy_version,
        risk_score=risk_score,
        risk_flags=risk_flags,
        prompt_preview=_preview(prompt_text),
        response_preview=_preview(response_text),
        token_input=token_input,
        token_output=token_output,
        latency_ms=latency_ms,
        status=status,
    )
    db.add(row)
    for rtype, meta in (risk_flags or {}).items():
        db.add(RiskEvent(
            request_id=request_id,
            risk_type=rtype,
            severity=meta.get("severity", "low"),
            description=str(meta.get("hits", ""))[:800],
            detector_version="v1",
        ))
    db.commit()
