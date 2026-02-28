from __future__ import annotations
import time, uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..db import get_db
from ..models.schemas import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChoice, ChatMessage, Usage
from .auth import require_api_key
from ..governance.policy_engine import PolicyEngine
from ..governance.detectors import run_detectors
from ..governance.risk_engine import score_risks
from ..governance.audit_service import write_audit
from ..execution.router import ModelRouter
from ..execution.limiter import InMemoryRateLimiter

router = APIRouter()
policy = PolicyEngine()
model_router = ModelRouter()
limiter = InMemoryRateLimiter()

def _get_department(req: Request) -> str:
    return req.headers.get("X-Department", "default")

@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(payload: ChatCompletionRequest, request: Request, api_key: str = Depends(require_api_key), db: Session = Depends(get_db)):
    dep = _get_department(request)
    p = policy.resolve(dep)

    rpm = int((p.get("rate_limit") or {}).get("rpm", 60))
    if not limiter.allow(api_key, rpm=rpm):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    detectors_enabled = (p.get("detectors") or {})
    prompt_text = "\n".join([f"{m.role}: {m.content}" for m in payload.messages])
    risk_flags = run_detectors(prompt_text, enabled=detectors_enabled)
    risk_score, _ = score_risks(risk_flags)

    route = p.get("route") or {}
    allowlist = set(route.get("models_allowlist") or [])
    if allowlist and payload.model not in allowlist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Model not allowed for department={dep}")

    providers = route.get("providers") or [{"name":"primary-mock","kind":"mock"}]

    t0 = time.time()
    try:
        reply, usage_dict, provider_name = await model_router.run(
            providers=providers,
            model=payload.model,
            messages=[m.model_dump() for m in payload.messages],
            temperature=payload.temperature or 0.2,
            max_tokens=payload.max_tokens or 512,
        )
        status_str = "ok"
    except Exception as e:
        reply = f"[error] {e}"
        usage_dict = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        provider_name = "none"
        status_str = "fail"

    latency_ms = int((time.time() - t0) * 1000)
    request_id = uuid.uuid4().hex

    write_audit(
        db,
        request_id=request_id,
        user_id=api_key,
        department=dep,
        model=payload.model,
        route_provider=provider_name,
        policy_version=policy.version,
        risk_score=risk_score,
        risk_flags=risk_flags,
        prompt_text=prompt_text,
        response_text=reply,
        token_input=int(usage_dict.get("prompt_tokens", 0)),
        token_output=int(usage_dict.get("completion_tokens", 0)),
        latency_ms=latency_ms,
        status=status_str,
    )

    if status_str != "ok":
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="All providers failed (see audit)")

    return ChatCompletionResponse(
        id=request_id,
        created=int(time.time()),
        model=payload.model,
        choices=[ChatCompletionChoice(index=0, message=ChatMessage(role="assistant", content=reply))],
        usage=Usage(
            prompt_tokens=int(usage_dict.get("prompt_tokens", 0)),
            completion_tokens=int(usage_dict.get("completion_tokens", 0)),
            total_tokens=int(usage_dict.get("total_tokens", 0)),
        ),
    )
