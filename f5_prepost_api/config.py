from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration settings for the F5 Pre/Post Check API."""
    PROJECT_NAME: str = "F5 Pre/Post Check API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # JWT Settings
    SECRET_KEY: str = "your-super-secret-key-for-development"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings() 