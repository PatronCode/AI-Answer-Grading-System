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
    
 
    
    # Path to questions.json
    QUESTIONS_PATH: str = os.getenv("QUESTIONS_PATH", "questions.json")
    
    model_config = {
        "env_file": ".env"
    }

settings = Settings()