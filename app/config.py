from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Smart Civic Services Platform"
    # NOT RECOMMENDED for production or public repositories
    MONGODB_URL: str = "mongodb+srv://ghotonaseer112_db_user:tm8QIwGUaYv0hR2n@class-practice.zhk9xms.mongodb.net/?appName=Class-practice"
    MONGODB_DB_NAME: str = "civic_services"
    GEMINI_API_KEY: str = "AQ.Ab8RN6LGOOAZG5S_7MFqwJRl8GrBdhPqGn5fhom78mWvbZBhVg"

    class Config:
        env_file = ".env"

settings = Settings()
