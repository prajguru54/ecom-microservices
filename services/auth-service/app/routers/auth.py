"""Authentication endpoints for user registration, login, and token management."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password, verify_token
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    TokenValidationRequest,
    TokenValidationResponse,
    UserLoginRequest,
    UserRegistrationRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserRegistrationRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Register a new user account.
    
    Args:
        user_data: User registration information
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    password_hash = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse.from_orm(new_user)


@router.post("/login", response_model=TokenResponse)
def login_user(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate user and return JWT token.
    
    Args:
        login_data: User login credentials
        db: Database session
        
    Returns:
        JWT access token with expiration info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == login_data.username) | (User.email == login_data.username)
    ).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,  # Convert to seconds
    )


@router.post("/validate", response_model=TokenValidationResponse)
def validate_token(token_data: TokenValidationRequest) -> TokenValidationResponse:
    """Validate a JWT token and return user information.
    
    Args:
        token_data: Token validation request
        
    Returns:
        Token validation result with user info if valid
    """
    payload = verify_token(token_data.token)
    
    if payload is None:
        return TokenValidationResponse(valid=False)
    
    # Extract user information from token
    user_id_str = payload.get("sub")
    username = payload.get("username")
    
    if not user_id_str:
        return TokenValidationResponse(valid=False)
    
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        return TokenValidationResponse(valid=False)
    
    return TokenValidationResponse(
        valid=True,
        user_id=user_id,
        username=username,
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(lambda: None),  # Placeholder for now
) -> UserResponse:
    """Get current authenticated user information.
    
    Note: This endpoint requires proper authentication middleware.
    For now, returns a placeholder response.
    
    Args:
        db: Database session
        current_user: Current authenticated user (from middleware)
        
    Returns:
        User information
    """
    # Placeholder implementation - in real usage, current_user would come from middleware
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return UserResponse.from_orm(current_user)