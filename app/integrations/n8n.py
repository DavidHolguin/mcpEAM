import httpx
from app.config import settings

async def trigger_webhook(webhook_path: str, data: dict, headers: dict | None = None):
    url = f"{settings.N8N_WEBHOOK_BASE.rstrip('/')}/{webhook_path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, json=data, headers=headers or {})
        r.raise_for_status()
        return {"status": r.status_code, "data": (r.json() if r.headers.get("content-type","{}").startswith("application/json") else r.text)}
