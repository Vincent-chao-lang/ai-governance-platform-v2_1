from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, Any, Type

# ---- Jira schemas ----
class JiraGetIssueParams(BaseModel):
    issue_key: str = Field(..., min_length=1)

class JiraSearchIssuesParams(BaseModel):
    jql: str = Field(..., min_length=1)
    max_results: int = Field(default=20, ge=1, le=100)

class JiraCreateIssueParams(BaseModel):
    project_key: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=4000)
    issue_type: str = Field(default="Task", min_length=1, max_length=64)

class JiraCommentIssueParams(BaseModel):
    issue_key: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1, max_length=4000)

# ---- ServiceNow schemas ----
class SNGetIncidentParams(BaseModel):
    number: str = Field(..., min_length=1)

class SNSearchIncidentsParams(BaseModel):
    query: str = Field(default="active=true", max_length=2000)
    limit: int = Field(default=20, ge=1, le=200)

class SNCreateIncidentParams(BaseModel):
    short_description: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=4000)
    urgency: str = Field(default="", max_length=10)
    impact: str = Field(default="", max_length=10)

class SNUpdateIncidentParams(BaseModel):
    sys_id: str = Field(..., min_length=1)
    fields: Dict[str, Any] = Field(..., min_length=1)

TOOL_PARAM_MODELS: Dict[str, Type[BaseModel]] = {
    "jira.get_issue": JiraGetIssueParams,
    "jira.search_issues": JiraSearchIssuesParams,
    "jira.create_issue": JiraCreateIssueParams,
    "jira.comment_issue": JiraCommentIssueParams,
    "servicenow.get_incident": SNGetIncidentParams,
    "servicenow.search_incidents": SNSearchIncidentsParams,
    "servicenow.create_incident": SNCreateIncidentParams,
    "servicenow.update_incident": SNUpdateIncidentParams,
}

def validate_tool_params(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    model = TOOL_PARAM_MODELS.get(tool_name)
    if not model:
        raise ValueError(f"No schema registered for tool: {tool_name}")
    obj = model.model_validate(params)
    return obj.model_dump()
