import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Smart Civic Services Platform"
    MONGODB_URL: str = os.environ.get("MONGODB_URL", "")
    MONGODB_DB_NAME: str = os.environ.get("MONGODB_DB_NAME", "civic_services")
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")

    class Config:
        env_file = ".env"

settings = Settings()
