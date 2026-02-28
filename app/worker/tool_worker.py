from __future__ import annotations
import asyncio
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models.db_models import ToolApproval
from ..execution.tool_proxy import ToolProxy, params_hash
from ..governance.tool_audit import write_tool_call

proxy = ToolProxy()

async def execute_approved_tool(approval_id: str):
    db: Session = SessionLocal()
    try:
        approval = db.get(ToolApproval, approval_id)
        if not approval or approval.status != "approved":
            return

        # mark as processing
        approval.status = "processing"
        db.commit()

        tool_request_id = approval.id  # reuse approval id for linkage

        try:
            result = await proxy.execute(approval.tool_name, approval.params_json)

            write_tool_call(
                db,
                request_id=tool_request_id,
                parent_request_id=approval.parent_request_id,
                tool_name=approval.tool_name,
                action_type=approval.action_type,
                allowed=True,
                parameters_hash=approval.parameters_hash,
                execution_time_ms=0,
            )

            approval.status = "completed"
            db.commit()

        except Exception as e:
            approval.status = "failed"
            approval.decision_note = str(e)
            db.commit()

    finally:
        db.close()

def enqueue_execution(approval_id: str):
    asyncio.create_task(execute_approved_tool(approval_id))
