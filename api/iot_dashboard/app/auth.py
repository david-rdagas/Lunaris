"""
Autenticación por API key.
Se acepta en:
  - Header:       X-API-Key: <key>
  - Query param:  ?api_key=<key>
"""
from fastapi import Header, Query, HTTPException, status
from app.config import settings


async def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    api_key:   str | None = Query(default=None),
) -> str:
    key = x_api_key or api_key
    if key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida o ausente",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return key
