from __future__ import annotations
import base64, csv, io
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from ..config import settings
from ..db import get_db
from ..models.db_models import AIRequest, AIToolCall, ToolApproval

router = APIRouter()

def _basic_auth_ok(req: Request) -> bool:
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Basic "):
        return False
    try:
        raw = base64.b64decode(auth.split(" ", 1)[1]).decode("utf-8")
        user, pwd = raw.split(":", 1)
        return (user == settings.admin_username and pwd == settings.admin_password)
    except Exception:
        return False

def require_admin(req: Request):
    if not _basic_auth_ok(req):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})

@router.get("/admin", response_class=HTMLResponse)
def admin_home(req: Request, db: Session = Depends(get_db)):
    require_admin(req)
    rows = db.execute(select(AIRequest).order_by(desc(AIRequest.ts)).limit(50)).scalars().all()
    html = ["<h2>AI Audit — latest 50</h2>"]
    html.append('<p><a href="/admin/export.csv">Export CSV</a></p>')
    html.append("<table border=1 cellpadding=6>")
    html.append("<tr><th>ts</th><th>user</th><th>dept</th><th>model</th><th>provider</th><th>risk</th><th>status</th><th>prompt</th></tr>")
    for r in rows:
        html.append(f"<tr><td>{r.ts}</td><td>{r.user_id}</td><td>{r.department}</td><td>{r.model}</td><td>{r.route_provider}</td><td>{r.risk_score}</td><td>{r.status}</td><td>{(r.prompt_preview or '')[:120]}</td></tr>")
    html.append("</table>")
    return HTMLResponse("".join(html))

@router.get("/admin/export.csv")
def export_csv(req: Request, db: Session = Depends(get_db)):
    require_admin(req)
    rows = db.execute(select(AIRequest).order_by(desc(AIRequest.ts)).limit(2000)).scalars().all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id","ts","user_id","department","model","route_provider","policy_version","risk_score","status","latency_ms","token_input","token_output","prompt_preview","response_preview"])
    for r in rows:
        writer.writerow([r.id, r.ts, r.user_id, r.department, r.model, r.route_provider, r.policy_version, r.risk_score, r.status, r.latency_ms, r.token_input, r.token_output, r.prompt_preview, r.response_preview])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=audit_export.csv"})


@router.get("/admin/tools_export.csv")
def tool_calls_export(req: Request, db: Session = Depends(get_db)):
    require_admin(req)
    rows = db.execute(select(AIToolCall).order_by(desc(AIToolCall.id)).limit(5000)).scalars().all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id","request_id","tool_name","action_type","allowed","parameters_hash","execution_time_ms"])
    for r in rows:
        writer.writerow([r.id, r.request_id, r.tool_name, r.action_type, r.allowed, r.parameters_hash, r.execution_time_ms])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=tool_calls_export.csv"})


@router.get("/admin/approvals_export.csv")
def approvals_export(req: Request, db: Session = Depends(get_db)):
    require_admin(req)
    rows = db.execute(select(ToolApproval).order_by(desc(ToolApproval.created_at)).limit(5000)).scalars().all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id","created_at","parent_request_id","requested_by","tool_name","action_type","parameters_hash","status","decided_at","decided_by","decision_note"])
    for r in rows:
        writer.writerow([r.id, r.created_at, r.parent_request_id, r.requested_by, r.tool_name, r.action_type, r.parameters_hash, r.status, r.decided_at, r.decided_by, r.decision_note])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=approvals_export.csv"})
