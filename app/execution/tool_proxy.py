from __future__ import annotations
import os, hashlib, json
from typing import Any, Dict
import httpx

def params_hash(params: Dict[str, Any]) -> str:
    try:
        raw = json.dumps(params, sort_keys=True, ensure_ascii=False).encode("utf-8")
    except Exception:
        raw = repr(params).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:32]

class ToolProxy:
    def _require(self, *envs: str) -> None:
        missing = [e for e in envs if not (os.getenv(e) or "").strip()]
        if missing:
            raise RuntimeError(f"Tool provider not configured. Missing env: {', '.join(missing)}")

    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name.startswith("jira."):
            return await self._jira(tool_name, params)
        if tool_name.startswith("servicenow."):
            return await self._servicenow(tool_name, params)
        raise RuntimeError(f"Unknown tool: {tool_name}")

    async def _jira(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self._require("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")
        base = os.getenv("JIRA_BASE_URL").rstrip("/")
        email = os.getenv("JIRA_EMAIL").strip()
        token = os.getenv("JIRA_API_TOKEN").strip()
        auth = (email, token)

        async with httpx.AsyncClient(timeout=30) as client:
            if tool_name == "jira.get_issue":
                key = str(params.get("issue_key", "")).strip()
                if not key:
                    raise RuntimeError("Missing params.issue_key")
                r = await client.get(f"{base}/rest/api/3/issue/{key}", auth=auth)
                r.raise_for_status()
                return {"issue": r.json()}

            if tool_name == "jira.search_issues":
                jql = str(params.get("jql", "")).strip()
                if not jql:
                    raise RuntimeError("Missing params.jql")
                max_results = int(params.get("max_results", 20))
                r = await client.get(f"{base}/rest/api/3/search", auth=auth, params={"jql": jql, "maxResults": max_results})
                r.raise_for_status()
                return {"search": r.json()}

            if tool_name == "jira.create_issue":
                project_key = str(params.get("project_key", "")).strip()
                summary = str(params.get("summary", "")).strip()
                description = str(params.get("description", "")).strip()
                issue_type = str(params.get("issue_type", "Task")).strip() or "Task"
                if not project_key or not summary:
                    raise RuntimeError("Missing params.project_key or params.summary")
                payload = {"fields": {"project": {"key": project_key}, "summary": summary, "issuetype": {"name": issue_type}}}
                if description:
                    payload["fields"]["description"] = description
                r = await client.post(f"{base}/rest/api/3/issue", auth=auth, json=payload)
                r.raise_for_status()
                return {"created": r.json()}

            if tool_name == "jira.comment_issue":
                key = str(params.get("issue_key", "")).strip()
                body = str(params.get("body", "")).strip()
                if not key or not body:
                    raise RuntimeError("Missing params.issue_key or params.body")
                r = await client.post(f"{base}/rest/api/3/issue/{key}/comment", auth=auth, json={"body": body})
                r.raise_for_status()
                return {"commented": r.json()}

        raise RuntimeError(f"Unsupported Jira tool: {tool_name}")

    async def _servicenow(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self._require("SERVICENOW_BASE_URL", "SERVICENOW_USER", "SERVICENOW_PASSWORD")
        base = os.getenv("SERVICENOW_BASE_URL").rstrip("/")
        user = os.getenv("SERVICENOW_USER").strip()
        pwd = os.getenv("SERVICENOW_PASSWORD").strip()
        auth = (user, pwd)

        async with httpx.AsyncClient(timeout=30) as client:
            if tool_name == "servicenow.get_incident":
                number = str(params.get("number", "")).strip()
                if not number:
                    raise RuntimeError("Missing params.number")
                r = await client.get(f"{base}/api/now/table/incident", auth=auth,
                                     params={"sysparm_query": f"number={number}", "sysparm_limit": 1})
                r.raise_for_status()
                return {"incident": r.json()}

            if tool_name == "servicenow.search_incidents":
                query = str(params.get("query", "")).strip() or "active=true"
                limit = int(params.get("limit", 20))
                r = await client.get(f"{base}/api/now/table/incident", auth=auth,
                                     params={"sysparm_query": query, "sysparm_limit": limit})
                r.raise_for_status()
                return {"search": r.json()}

            if tool_name == "servicenow.create_incident":
                short_description = str(params.get("short_description", "")).strip()
                description = str(params.get("description", "")).strip()
                urgency = str(params.get("urgency", "")).strip()
                impact = str(params.get("impact", "")).strip()
                if not short_description:
                    raise RuntimeError("Missing params.short_description")
                payload = {"short_description": short_description}
                if description: payload["description"] = description
                if urgency: payload["urgency"] = urgency
                if impact: payload["impact"] = impact
                r = await client.post(f"{base}/api/now/table/incident", auth=auth, json=payload)
                r.raise_for_status()
                return {"created": r.json()}

            if tool_name == "servicenow.update_incident":
                sys_id = str(params.get("sys_id", "")).strip()
                fields = params.get("fields", {})
                if not sys_id or not isinstance(fields, dict) or not fields:
                    raise RuntimeError("Missing params.sys_id or params.fields")
                r = await client.patch(f"{base}/api/now/table/incident/{sys_id}", auth=auth, json=fields)
                r.raise_for_status()
                return {"updated": r.json()}

        raise RuntimeError(f"Unsupported ServiceNow tool: {tool_name}")
