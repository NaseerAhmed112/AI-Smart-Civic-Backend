import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Smart Civic Services Platform"
    MONGODB_URL: str = os.environ.get("MONGODB_URL", "")
    MONGODB_DB_NAME: str = os.environ.get("MONGODB_DB_NAME", "civic_services")
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    # Frontend origin (e.g. https://civic-frontend.vercel.app) used for CORS
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "")
    # Optional comma-separated list of allowed origins
    ALLOWED_ORIGINS: str = os.environ.get("ALLOWED_ORIGINS", "")

    class Config:
        env_file = ".env"

settings = Settings()
