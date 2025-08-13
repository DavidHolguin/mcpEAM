# MCP Server (FastAPI + Supabase + n8n)

## Estructura
- `main.py`: App FastAPI y healthcheck `/healthz`.
- `app/mcp/server.py`: Endpoint `/mcp` JSON-RPC 2.0 (`tools/list`, `tools/call`).
- `app/integrations/supabase.py`: Operaciones DB/Storage/Vector.
- `app/integrations/n8n.py`: Invocación de webhooks n8n.
- `app/security/auth.py`: API tokens por cabecera `x-api-key`.
- `app/config.py`: Carga de variables de entorno.
- `migrations/001_init.sql`: Esquema Supabase (session_state, tool_audit, vector_store, RPC `match_vectors`).
- `tools.schema.json`: Definiciones de herramientas MCP.

## Variables de entorno
Copiar `.env.example` a `.env` en local o configurar en Railway.

- `SUPABASE_URL`: URL del proyecto Supabase.
- `SUPABASE_SERVICE_ROLE_KEY`: clave service role (solo backend).
- `SUPABASE_ANON_KEY`: opcional.
- `N8N_WEBHOOK_BASE`: base de webhooks públicos de n8n, ej: `https://n8n.tu-dominio.com/webhook`.
- `MCP_API_TOKENS`: CSV de tokens válidos, ej: `token1,token2`.
- `ALLOW_ORIGINS`: lista CORS, ej: `https://mi-host-agente.com`.

## Desarrollo local (Windows PowerShell)
```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
$env:MCP_API_TOKENS="dev-token"
$env:SUPABASE_URL="https://xxxxx.supabase.co"
$env:SUPABASE_SERVICE_ROLE_KEY="eyJ..."
$env:N8N_WEBHOOK_BASE="https://n8n.tu-dominio.com/webhook"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Probar:
- `GET http://localhost:8000/healthz`
- `POST http://localhost:8000/mcp` con header `x-api-key: dev-token` y body:
```json
{"jsonrpc":"2.0","id":"1","method":"tools/list"}
```

## Despliegue en Railway
- Añadir servicio Dockerfile.
- Variables de entorno: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `N8N_WEBHOOK_BASE`, `MCP_API_TOKENS`, `ALLOW_ORIGINS`.
- Comando inicio: `uvicorn main:app --host 0.0.0.0 --port $PORT --proxy-headers`.
- Healthcheck: `/healthz`.
- Escalado horizontal: habilitar auto-scale; la app es stateless.

## Migraciones Supabase
Ejecutar `migrations/001_init.sql` en el SQL Editor de Supabase.

## Seguridad
- Mantener Service Role solo en backend.
- Rotar `MCP_API_TOKENS` periódicamente.
- Opcional: firmar requests con HMAC y timestamp para antireplay.
