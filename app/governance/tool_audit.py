from __future__ import annotations
from sqlalchemy.orm import Session
from ..models.db_models import AIToolCall

def write_tool_call(
    db: Session,
    *,
    request_id: str,
    parent_request_id: str | None,
    tool_name: str,
    action_type: str,
    allowed: bool,
    parameters_hash: str,
    execution_time_ms: int,
):
    db.add(AIToolCall(
        request_id=request_id,
        parent_request_id=parent_request_id,
        tool_name=tool_name,
        action_type=action_type,
        allowed=allowed,
        parameters_hash=parameters_hash,
        execution_time_ms=execution_time_ms,
    ))
    db.commit()
