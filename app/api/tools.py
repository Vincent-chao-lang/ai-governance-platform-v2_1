from __future__ import annotations
import time, uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..db import get_db
from .auth import require_api_key
from .admin import require_admin  # reuse BasicAuth for approvals
from ..governance.policy_engine import PolicyEngine
from ..governance.tool_guard import check_tool_allowed
from ..governance.tool_audit import write_tool_call
from ..governance.tool_registry import validate_tool_params
from ..governance.approval_service import create_approval, decide_approval
from ..worker.tool_worker import enqueue_execution
from ..execution.tool_proxy import ToolProxy, params_hash
from ..models.tool_schemas import ToolExecuteRequest, ToolExecuteResponse

router = APIRouter()
policy = PolicyEngine()
proxy = ToolProxy()

def _get_department(req: Request) -> str:
    return req.headers.get("X-Department", "default")

def _approval_required(p: dict, tool_name: str) -> bool:
    tools = p.get("tools") or {}
    approval = tools.get("approval") or {}
    if not approval:
        return False
    if not approval.get("required_for_write", False):
        return False
    bypass = set(approval.get("bypass_tools") or [])
    return tool_name not in bypass

@router.post("/v1/tools/execute", response_model=ToolExecuteResponse)
async def tools_execute(payload: ToolExecuteRequest, request: Request, api_key: str = Depends(require_api_key), db: Session = Depends(get_db)):
    dep = _get_department(request)
    p = policy.resolve(dep)

    allowed, reason = check_tool_allowed(p, tool_name=payload.tool_name, action_type=payload.action_type)
    tool_request_id = uuid.uuid4().hex

    # 1) policy block
    if not allowed:
        write_tool_call(
            db,
            request_id=tool_request_id,
            parent_request_id=payload.parent_request_id,
            tool_name=payload.tool_name,
            action_type=payload.action_type,
            allowed=False,
            parameters_hash=params_hash(payload.params),
            execution_time_ms=0,
        )
        return ToolExecuteResponse(
            request_id=tool_request_id,
            parent_request_id=payload.parent_request_id,
            tool_name=payload.tool_name,
            action_type=payload.action_type,
            allowed=False,
            blocked_reason=reason,
            result={},
        )

    # 2) schema validation
    try:
        clean_params = validate_tool_params(payload.tool_name, payload.params)
    except Exception as e:
        write_tool_call(
            db,
            request_id=tool_request_id,
            parent_request_id=payload.parent_request_id,
            tool_name=payload.tool_name,
            action_type=payload.action_type,
            allowed=False,
            parameters_hash=params_hash(payload.params),
            execution_time_ms=0,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Tool params schema invalid: {e}")

    ph = params_hash(clean_params)

    # 3) approval for WRITE
    if payload.action_type == "WRITE" and _approval_required(p, payload.tool_name):
        approval_id = uuid.uuid4().hex
        create_approval(
            db,
            approval_id=approval_id,
            parent_request_id=payload.parent_request_id,
            requested_by=api_key,
            tool_name=payload.tool_name,
            action_type=payload.action_type,
            parameters_hash=ph,
            params_json=clean_params,
        )
        write_tool_call(
            db,
            request_id=tool_request_id,
            parent_request_id=payload.parent_request_id,
            tool_name=payload.tool_name,
            action_type=payload.action_type,
            allowed=False,
            parameters_hash=ph,
            execution_time_ms=0,
        )
        return ToolExecuteResponse(
            request_id=tool_request_id,
            parent_request_id=payload.parent_request_id,
            tool_name=payload.tool_name,
            action_type=payload.action_type,
            allowed=False,
            blocked_reason="approval_required",
            approval_id=approval_id,
            approval_status="pending",
            result={},
        )

    # 4) execute tool
    t0 = time.time()
    try:
        result = await proxy.execute(payload.tool_name, clean_params)
        ms = int((time.time() - t0) * 1000)
        write_tool_call(
            db,
            request_id=tool_request_id,
            parent_request_id=payload.parent_request_id,
            tool_name=payload.tool_name,
            action_type=payload.action_type,
            allowed=True,
            parameters_hash=ph,
            execution_time_ms=ms,
        )
        return ToolExecuteResponse(
            request_id=tool_request_id,
            parent_request_id=payload.parent_request_id,
            tool_name=payload.tool_name,
            action_type=payload.action_type,
            allowed=True,
            result=result,
        )
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        write_tool_call(
            db,
            request_id=tool_request_id,
            parent_request_id=payload.parent_request_id,
            tool_name=payload.tool_name,
            action_type=payload.action_type,
            allowed=True,
            parameters_hash=ph,
            execution_time_ms=ms,
        )
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Tool execution failed: {e}")

# ---- Approval APIs (Admin only) ----
@router.post("/admin/approvals/{approval_id}/approve")
def approve_tool(approval_id: str, req: Request, db: Session = Depends(get_db)):
    require_admin(req)
    row = decide_approval(db, approval_id=approval_id, decision="approved", decided_by="admin", note="")
    enqueue_execution(row.id)
    return {"id": row.id, "status": row.status, "async_execution": "queued"}

@router.post("/admin/approvals/{approval_id}/reject")
def reject_tool(approval_id: str, req: Request, db: Session = Depends(get_db)):
    require_admin(req)
    row = decide_approval(db, approval_id=approval_id, decision="rejected", decided_by="admin", note="")
    return {"id": row.id, "status": row.status}
