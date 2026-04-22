"""Pydantic schemas for authentication endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegistrationRequest(BaseModel):
    """Schema for user registration request."""

    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")


class UserLoginRequest(BaseModel):
    """Schema for user login request."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenValidationRequest(BaseModel):
    """Schema for token validation request."""

    token: str = Field(..., description="JWT token to validate")


class TokenValidationResponse(BaseModel):
    """Schema for token validation response."""

    valid: bool = Field(..., description="Whether the token is valid")
    user_id: uuid.UUID | None = Field(default=None, description="User ID if token is valid")
    username: str | None = Field(default=None, description="Username if token is valid")


class UserResponse(BaseModel):
    """Schema for user information response."""

    id: uuid.UUID = Field(..., description="User unique identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Account last update timestamp")

    class Config:
        """Pydantic configuration."""
        
        from_attributes = True