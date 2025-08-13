from fastapi import FastAPI
from app.mcp.server import router as mcp_router
from app.security.auth import with_cors

app = FastAPI(title="MCP Server", version="1.0.0")

with_cors(app)

@app.get("/")
async def root():
    return {"name": "MCP Server", "status": "ok"}

@app.post("/")
async def root_post():
    # Some scanners/integrations may POST to root; guide them to /mcp
    return {"message": "Use POST /mcp with JSON-RPC 2.0 (methods: tools/list, tools/call)"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

app.include_router(mcp_router)
