"""Application configuration using Pydantic settings.

This module defines the application settings schema and loads configuration
from environment variables via a .env file.
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All settings are loaded from environment variables or a .env file.
    Required settings must be set, optional settings have defaults.
    """
    
    # MongoDB Configuration
    mongodb_uri: str  #: MongoDB connection URI (required)
    database_name: str = "rootbeer_reviews"  #: Database name (default: "rootbeer_reviews")
    
    # Security
    secret_key: str  #: Secret key for JWT token signing (required)
    algorithm: str = "HS256"  #: JWT algorithm (default: "HS256")
    
    # Admin Configuration (optional - only needed for initial admin user creation)
    admin_email: Optional[str] = None  #: Admin email for initial user creation (optional)
    admin_password: Optional[str] = None  #: Admin password for initial user creation (optional)
    
    # AWS S3 Configuration (for image uploads)
    aws_access_key_id: Optional[str] = None  #: AWS access key ID for S3 (optional)
    aws_secret_access_key: Optional[str] = None  #: AWS secret access key for S3 (optional)
    aws_region: str = "us-east-1"  #: AWS region for S3 (default: "us-east-1")
    s3_bucket_name: Optional[str] = None  #: S3 bucket name for image storage (optional)
    
    # Environment
    environment: str = "development"  #: Application environment (default: "development")
    
    model_config = ConfigDict(
        env_file=".env",  #: Path to .env file
        case_sensitive=False,  #: Environment variable names are case-insensitive
    )


# Global settings instance
settings = Settings()

