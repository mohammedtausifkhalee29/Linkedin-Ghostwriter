"""Application configuration settings."""

import os
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent.parent / ".env"),  # Look for .env in project root
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Project Info
    PROJECT_NAME: str = "LinkedIn Ghostwriter API"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:8501"])
    
    # Database - Use absolute path to avoid path resolution issues
    DATABASE_URL: str = Field(
        default=f"sqlite:///{Path(__file__).parent.parent.parent.parent / 'database' / 'linkedin_ghostwriter.db'}"
    )
    
    # AI/LLM
    OPENAI_API_KEY: str = Field(default="")
    LLM_MODEL: str = Field(default="gpt-4")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(default="")
    
    # Email/SMTP
    SMTP_HOST: str = Field(default="")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    SMTP_FROM_EMAIL: str = Field(default="")


settings = Settings()
