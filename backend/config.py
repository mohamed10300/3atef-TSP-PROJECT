from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenRouter
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL: str = "openai/gpt-4o"

    # Database
    DATABASE_URL: str = "sqlite:///./3atef_dev.db"
    DATABASE_URL_SQLITE: str = "sqlite:///./3atef_dev.db"

    @field_validator("DATABASE_URL")
    @classmethod
    def fix_postgres_scheme(cls, v: str) -> str:
        # Render provides postgres:// but SQLAlchemy 2.0 requires postgresql://
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    # Email — Outlook
    OUTLOOK_CLIENT_ID: str = ""
    OUTLOOK_CLIENT_SECRET: str = ""
    OUTLOOK_TENANT_ID: str = ""

    # Email — Gmail
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""

    # App
    ENVIRONMENT: str = "development"
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    # Comma-separated extra origins to allow (e.g. Vercel preview URLs)
    ALLOWED_ORIGINS: str = ""
    SECRET_KEY: str = "changeme"

    # Scraping
    SCRAPER_HEADLESS: bool = True
    SCRAPER_TIMEOUT: int = 30000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
