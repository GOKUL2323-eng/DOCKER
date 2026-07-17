import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Shadow AI"
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "shadow_ai_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_cyber_key_999")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    RAPID_API_KEY: str = os.getenv("RAPID_API_KEY", "")
    GOOGLE_TTS_API_KEY: str = os.getenv("GOOGLE_TTS_API_KEY", "")
    IMAGE_GEN_API_KEY: str = os.getenv("IMAGE_GEN_API_KEY", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")


    class Config:
        case_sensitive = True

settings = Settings()
