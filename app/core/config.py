"""
Application Configuration

Manages environment variables, settings, and configuration for the entire application.
Uses Pydantic for type-safe configuration management.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class defines all configuration options for our application.
    Values can be set via environment variables or .env file.
    """
    
    # Application settings
    app_name: str = "AI Business Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    database_url: Optional[str] = "sqlite:///./ai_business_assistant.db"  # Default to SQLite for development
    
    # Security settings
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI/LLM settings
    openai_api_key: Optional[str] = None
    embedding_model: str = "all-MiniLM-L6-v2"  # Sentence transformer model
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".pdf"]
    upload_directory: str = "./uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings