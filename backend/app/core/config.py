"""
Application configuration settings.
"""

import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Image2Model"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://frontend:3000"

    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "image2model"
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/image2model"

    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # File storage settings
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "results"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    
    # Model settings
    MODEL_CACHE_DIR: str = "models"
    DEFAULT_MODEL: str = "depth_anything_v2"
    MAX_IMAGE_SIZE: int = 1024
    
    # Worker settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    
    # FAL.AI Configuration
    FAL_API_KEY: str = "your-fal-api-key-here"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()