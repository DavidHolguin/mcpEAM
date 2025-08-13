from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_ANON_KEY: str | None = None
    N8N_WEBHOOK_BASE: str
    MCP_API_TOKENS: str  # CSV de tokens válidos
    ALLOW_ORIGINS: str = "*"
    ENV: str = "production"

    class Config:
        env_file = ".env"

settings = Settings()
