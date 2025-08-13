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
    api_key = request.headers.get("x-api-key")
    allowed = {t.strip() for t in settings.MCP_API_TOKENS.split(",") if t.strip()}
    if not api_key or api_key not in allowed:
        raise HTTPException(status_code=401, detail="invalid api key")
    return True
