from fastapi import Request, HTTPException
from starlette.middleware.cors import CORSMiddleware
from app.config import settings

def with_cors(app):
    allow = [o.strip() for o in settings.ALLOW_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def validate_api_key(request: Request, needed_scope: str | None = None):
    # Prefer custom header
    api_key = request.headers.get("x-api-key")
    # Also accept Authorization: Bearer <token>
    auth = request.headers.get("authorization")
    bearer_token = None
    if auth:
        parts = auth.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            bearer_token = parts[1]

    token = api_key or bearer_token
    allowed = {t.strip() for t in settings.MCP_API_TOKENS.split(",") if t.strip()}
    if not token or token not in allowed:
        raise HTTPException(status_code=401, detail="invalid api key")
    return True
