from __future__ import annotations
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ..db import Base

class AIRequest(Base):
    __tablename__ = "ai_requests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    department: Mapped[str] = mapped_column(String(128), index=True)

    model: Mapped[str] = mapped_column(String(128), index=True)
    route_provider: Mapped[str] = mapped_column(String(64))
    policy_version: Mapped[str] = mapped_column(String(64))

    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_flags: Mapped[dict] = mapped_column(JSON, default=dict)

    prompt_preview: Mapped[str] = mapped_column(Text, default="")
    response_preview: Mapped[str] = mapped_column(Text, default="")

    token_input: Mapped[int] = mapped_column(Integer, default=0)
    token_output: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(32), default="ok", index=True)

    tool_calls: Mapped[list["AIToolCall"]] = relationship(back_populates="request", cascade="all,delete-orphan")
    risk_events: Mapped[list["RiskEvent"]] = relationship(back_populates="request", cascade="all,delete-orphan")

class AIToolCall(Base):
    __tablename__ = "ai_tool_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("ai_requests.id"), index=True)

    # Optional linkage to an LLM request id (ai_requests.id)
    parent_request_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    tool_name: Mapped[str] = mapped_column(String(128))
    action_type: Mapped[str] = mapped_column(String(16))
    allowed: Mapped[bool] = mapped_column(Boolean, default=False)

    parameters_hash: Mapped[str] = mapped_column(String(128), default="")
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0)

    request: Mapped["AIRequest"] = relationship(back_populates="tool_calls")

class RiskEvent(Base):
    __tablename__ = "risk_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(ForeignKey("ai_requests.id"), index=True)

    risk_type: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(16))
    description: Mapped[str] = mapped_column(Text, default="")
    detector_version: Mapped[str] = mapped_column(String(64), default="v1")

    request: Mapped["AIRequest"] = relationship(back_populates="risk_events")

class PolicyVersion(Base):
    __tablename__ = "policy_versions"

    version_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(String(128), default="system")
    change_note: Mapped[str] = mapped_column(Text, default="")


class ToolApproval(Base):
    __tablename__ = "tool_approvals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    parent_request_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    requested_by: Mapped[str] = mapped_column(String(128), index=True)

    tool_name: Mapped[str] = mapped_column(String(128))
    action_type: Mapped[str] = mapped_column(String(16))  # WRITE typically
    parameters_hash: Mapped[str] = mapped_column(String(128), default="")
    params_json: Mapped[dict] = mapped_column(JSON, default=dict)

    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)  # pending/approved/rejected/processing/completed/failed
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    decided_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    decision_note: Mapped[str] = mapped_column(Text, default="")
