from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///./3atef_dev.db"
    DATABASE_URL_SQLITE: str = "sqlite:///./3atef_dev.db"

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
    SECRET_KEY: str = "changeme"

    # Scraping
    SCRAPER_HEADLESS: bool = True
    SCRAPER_TIMEOUT: int = 30000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
