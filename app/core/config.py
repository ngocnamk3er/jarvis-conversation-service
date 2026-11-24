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

    # Admission control (app/core/load_shed.py): past this many requests in flight in this process, the next one is
    # refused at once with 503 + Retry-After instead of waiting. 15 is the size of the database connection pool
    # (SQLAlchemy's default: 5 + 10 overflow). A request past it would wait for a connection, up to 30 s by default,
    # when a refusal now costs the caller one second. Per process: with more replicas the total is that many times as
    # much, and so is the number of Postgres connections (max_connections is 100, shared). 0 = no limit.
    LOAD_SHED_ENABLED: bool = True
    LOAD_SHED_MAX_INFLIGHT: int = 15
    LOAD_SHED_RETRY_AFTER_SECONDS: int = 1

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
