from __future__ import annotations
from fastapi import Header, HTTPException, status
from ..config import settings

def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    if not x_api_key or x_api_key not in set(settings.allowed_api_keys):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return x_api_key
