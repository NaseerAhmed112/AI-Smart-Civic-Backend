import os
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Smart Civic Services Platform"
    MONGODB_URL: str = Field("", env=("MONGODB_URL", "MONGO_URI"))
    MONGODB_DB_NAME: str = Field("civic_services", env="MONGODB_DB_NAME")
    GEMINI_API_KEY: str = Field("", env="GEMINI_API_KEY")
    # Frontend origin (e.g. https://civic-frontend.vercel.app) used for CORS
    FRONTEND_URL: str = Field("", env="FRONTEND_URL")
    # Optional comma-separated list of allowed origins
    ALLOWED_ORIGINS: str = Field("", env="ALLOWED_ORIGINS")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
