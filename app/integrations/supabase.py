import base64
from typing import Any, Dict
from supabase import create_client, Client
from app.config import settings

_sb: Client | None = None

def client() -> Client:
    global _sb
    if _sb is None:
        _sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _sb

async def query(p: Dict[str, Any]) -> Dict[str, Any]:
    sb = client()
    sel = ",".join(p.get("columns") or ["*"])
    q = sb.table(p["table_name"]).select(sel)
    for k, v in (p.get("filters") or {}).items():
        q = q.eq(k, v)
    if p.get("order_by"):
        q = q.order(p["order_by"], desc=not p.get("ascending", True))
    limit = int(p.get("limit", 100))
    offset = int(p.get("offset", 0))
    q = q.range(offset, offset + limit - 1)
    res = q.execute()
    return {"data": res.data}

async def insert(p: Dict[str, Any]) -> Dict[str, Any]:
    sb = client()
    res = sb.table(p["table_name"]).insert(p["data"]).execute()
    return {"data": res.data}

async def update(p: Dict[str, Any]) -> Dict[str, Any]:
    sb = client()
    q = sb.table(p["table_name"]).update(p["data"])
    for k, v in (p.get("filters") or {}).items():
        q = q.eq(k, v)
    res = q.execute()
    return {"data": res.data}

async def delete(p: Dict[str, Any]) -> Dict[str, Any]:
    sb = client()
    q = sb.table(p["table_name"]).delete()
    for k, v in (p.get("filters") or {}).items():
        q = q.eq(k, v)
    res = q.execute()
    return {"data": res.data}

async def upload_file(p: Dict[str, Any]) -> Dict[str, Any]:
    sb = client()
    content = base64.b64decode(p["content_base64"])
    sb.storage.from_(p["bucket"]).upload(p["path"], content, {"content-type": p.get("content_type","application/octet-stream")})
    signed = sb.storage.from_(p["bucket"]).create_signed_url(p["path"], 3600)
    return {"signed_url": signed.get("signedURL") or signed.get("signed_url")}

async def download_file(p: Dict[str, Any]) -> Dict[str, Any]:
    sb = client()
    signed = sb.storage.from_(p["bucket"]).create_signed_url(p["path"], int(p.get("expires", 3600)))
    return {"signed_url": signed.get("signedURL") or signed.get("signed_url")}

async def list_files(p: Dict[str, Any]) -> Dict[str, Any]:
    sb = client()
    files = sb.storage.from_(p["bucket"]).list(path=p.get("prefix",""), limit=int(p.get("limit",100)))
    return {"files": files}

async def vector_upsert(p: Dict[str, Any]) -> Dict[str, Any]:
    sb = client()
    res = sb.table("vector_store").upsert({
        "namespace": p["namespace"],
        "ref": p["ref"],
        "embedding": p["embedding"],
        "metadata": p.get("metadata", {})
    }).execute()
    return {"data": res.data}

async def vector_query(p: Dict[str, Any]) -> Dict[str, Any]:
    sb = client()
    res = sb.rpc("match_vectors", {"ns": p["namespace"], "query": p["embedding"], "top_k": int(p.get("top_k",5))}).execute()
    return {"matches": res.data}
