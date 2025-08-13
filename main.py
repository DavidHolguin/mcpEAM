from fastapi import FastAPI
from app.mcp.server import router as mcp_router
from app.security.auth import with_cors

app = FastAPI(title="MCP Server", version="1.0.0")

with_cors(app)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

app.include_router(mcp_router)
