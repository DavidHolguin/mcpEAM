from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from app.models.schemas import JSONRPCRequest, JSONRPCResponse
from app.security.auth import validate_api_key
from app.integrations import supabase as sb
from app.integrations import n8n as n8n_integ
import json
from pathlib import Path

router = APIRouter()

TOOLS = {
    "supabase/query": sb.query,
    "supabase/insert": sb.insert,
    "supabase/update": sb.update,
    "supabase/delete": sb.delete,
    "supabase/uploadFile": sb.upload_file,
    "supabase/downloadFile": sb.download_file,
    "supabase/listFiles": sb.list_files,
    "supabase/vectorUpsert": sb.vector_upsert,
    "supabase/vectorQuery": sb.vector_query,
    "n8n/triggerWebhook": lambda p: n8n_integ.trigger_webhook(p["webhook_path"], p.get("data", {}), p.get("headers"))
}

@router.get("/mcp")
async def mcp_get():
    # Friendly GET for scanners/browsers
    return JSONResponse({
        "name": "MCP Server",
        "version": "1.0.0",
        "message": "Use POST /mcp with JSON-RPC 2.0 (methods: tools/list, tools/call).",
        "schema": "/mcp/schema"
    })

@router.get("/mcp/schema")
async def mcp_schema():
    # Serve tools schema to help integrations discover available tools
    root = Path(__file__).resolve().parents[2]
    schema_path = root / "tools.schema.json"
    if not schema_path.exists():
        raise HTTPException(status_code=404, detail="schema not found")
    with schema_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return JSONResponse(data)

@router.post("/mcp")
async def mcp(request: Request):
    body = await request.json()
    rpc = JSONRPCRequest(**body)
    if rpc.method == "tools/list":
        validate_api_key(request)
        return JSONResponse(JSONRPCResponse(result=list(TOOLS.keys()), id=rpc.id).model_dump())
    if rpc.method == "tools/call":
        validate_api_key(request)
        params = rpc.params or {}
        name = params.get("name")
        p = params.get("parameters") or {}
        if name not in TOOLS:
            raise HTTPException(status_code=400, detail="unknown tool")
        handler = TOOLS[name]

        async def stream():
            yield b'{"jsonrpc":"2.0","id":' + json.dumps(rpc.id).encode() + b',"result":{"stream":['
            result = await handler(p)
            yield json.dumps({"event":"result","data":result}).encode()
            yield b"]}}"
        return StreamingResponse(stream(), media_type="application/json")

    return JSONResponse(JSONRPCResponse(error={"code":-32601,"message":"Method not found"}, id=rpc.id).model_dump())
