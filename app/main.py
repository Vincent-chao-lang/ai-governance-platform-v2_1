from __future__ import annotations
from fastapi import FastAPI
from .db import init_db
from .api.chat import router as chat_router
from .api.admin import router as admin_router
from .api.health import router as health_router
from .api.tools import router as tools_router

app = FastAPI(title="AI Governance Platform (V2.4)", version="0.1.4")

@app.on_event("startup")
def _startup():
    init_db()

app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(health_router)
app.include_router(tools_router)
