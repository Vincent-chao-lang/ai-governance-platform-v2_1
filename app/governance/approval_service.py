from __future__ import annotations
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any
from ..models.db_models import ToolApproval

def create_approval(
    db: Session,
    *,
    approval_id: str,
    parent_request_id: str | None,
    requested_by: str,
    tool_name: str,
    action_type: str,
    parameters_hash: str,
    params_json: Dict[str, Any],
) -> ToolApproval:
    row = ToolApproval(
        id=approval_id,
        parent_request_id=parent_request_id,
        requested_by=requested_by,
        tool_name=tool_name,
        action_type=action_type,
        parameters_hash=parameters_hash,
        params_json=params_json,
        status="pending",
    )
    db.add(row)
    db.commit()
    return row

def decide_approval(
    db: Session,
    *,
    approval_id: str,
    decision: str,  # approved/rejected
    decided_by: str,
    note: str = "",
) -> ToolApproval:
    row = db.get(ToolApproval, approval_id)
    if not row:
        raise ValueError("approval not found")
    if row.status != "pending":
        return row
    row.status = decision
    row.decided_by = decided_by
    row.decided_at = datetime.utcnow()
    row.decision_note = note or ""
    db.commit()
    return row
