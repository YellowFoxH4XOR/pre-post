import os
from typing import Dict, Any

# Fix for Pydantic v2 compatibility
try:
    # First try the new location (Pydantic v2)
    from pydantic_settings import BaseSettings
except ImportError:
    # Fall back to the old location (Pydantic v1)
    from pydantic import BaseSettings

class Settings(BaseSettings):
    """Configuration settings for the F5 Pre/Post Check API."""
    PROJECT_NAME: str = "F5 Pre/Post Check API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("APP_ENVIRONMENT", "development")
    
    # JWT Settings
    SECRET_KEY: str = "your-super-secret-key-for-development"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    DB_ECHO: bool = True
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Define model configuration
    model_config: Dict[str, Any] = {
        "env_file": ".env",
    }

settings = Settings() 