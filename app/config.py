"""Application configuration using Pydantic settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MongoDB Configuration
    mongodb_uri: str
    database_name: str = "rootbeer_reviews"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    
    # Admin Configuration (optional - only needed for initial admin user creation)
    admin_email: Optional[str] = None
    admin_password: Optional[str] = None
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

