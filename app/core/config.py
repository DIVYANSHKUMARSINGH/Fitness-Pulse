from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FitnessPulse API"
    VERSION: str = "1.0.0"
    GEMINI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./fitnesspulse.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
