from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General
    app_name: str = "Social AI Manager"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me"

    # URLs
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    api_v1_prefix: str = "/api/v1"

    # Database (Coolify entrega postgres:// — se normaliza a asyncpg)
    database_url: str = "postgresql+asyncpg://social_manager:social_manager_secret@postgres:5432/social_manager"
    run_migrations: bool = True
    run_seed: bool = False

    # Redis
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    # JWT
    jwt_secret: str = "change-me-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Encryption
    encryption_key: str = "change-me-32-byte-base64-encoded-key"

    # Meta / Instagram
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_redirect_uri: str = "http://localhost:8000/api/v1/social/instagram/callback"
    meta_graph_api_version: str = "v21.0"
    meta_access_token: str = ""

    # AI Providers
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    replicate_api_token: str = ""
    stability_api_key: str = ""
    nano_banana_api_key: str = ""

    # Rate limiting
    rate_limit_per_minute: int = 60

    # CORS
    cors_origins: str = "http://localhost:3000"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Coolify suele entregar postgres:// — normalizar para SQLAlchemy async."""
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            if v.startswith("postgresql://") and "+asyncpg" not in v and "+psycopg" not in v:
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def database_url_sync(self) -> str:
        """URL síncrona para Alembic offline mode."""
        url = self.database_url
        if "+asyncpg" in url:
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        if url.startswith("postgresql://") and "+psycopg" not in url:
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def meta_graph_base_url(self) -> str:
        return f"https://graph.facebook.com/{self.meta_graph_api_version}"


settings = Settings()
