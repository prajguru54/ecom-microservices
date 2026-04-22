"""Configuration settings for auth-service."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Service configuration
    service_name: str = Field(default="auth-service")
    service_port: int = Field(default=8001)
    
    # Database configuration
    database_url: str = Field(
        default="postgresql+psycopg://ecom_user:change_me@localhost:5434/auth_db"
    )
    
    # JWT configuration
    jwt_secret_key: str = Field(default="change_me")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    
    # Security configuration
    password_hash_rounds: int = Field(default=12)


settings = Settings()