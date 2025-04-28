import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "Exam Answer Marking API"
    APP_VERSION: str = "1.0.0"
    
    # OpenAI API settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # MongoDB settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb+srv://Icode:87654321@cluster0.7jrtb.mongodb.net/exam_marking_db")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "exam_marking_db")
    
    # JWT settings for authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-token-generation")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Path to questions.json
    QUESTIONS_PATH: str = os.getenv("QUESTIONS_PATH", "questions.json")
    
    model_config = {
        "env_file": ".env"
    }

settings = Settings()
