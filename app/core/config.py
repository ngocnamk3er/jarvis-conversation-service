from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Jarvis Conversation Service"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql://jarvis:jarvis@localhost:5433/jarvis_conversations"

    # Shared secret jarvis-backend sends on every call — this service is
    # internal-only (never reachable from the frontend/ingress), so a plain
    # header check is enough; it doesn't need its own JWKS/JWT verification.
    INTERNAL_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
