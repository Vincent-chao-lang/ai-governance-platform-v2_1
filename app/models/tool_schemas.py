from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

ActionType = Literal["READ", "WRITE"]

class ToolExecuteRequest(BaseModel):
    parent_request_id: str | None = Field(default=None, description="LLM request id to bind tool call for audit replay")
    tool_name: str = Field(..., examples=["jira.get_issue", "servicenow.create_incident"])
    action_type: ActionType
    params: Dict[str, Any] = Field(default_factory=dict)

class ToolExecuteResponse(BaseModel):
    parent_request_id: str | None = None
    approval_id: str | None = None
    approval_status: str | None = None
    request_id: str
    tool_name: str
    action_type: ActionType
    allowed: bool
    blocked_reason: Optional[str] = None
    result: Dict[str, Any] = Field(default_factory=dict)
