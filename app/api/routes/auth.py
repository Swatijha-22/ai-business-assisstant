"""
Authentication API Routes

Handles user registration, login, and authentication-related endpoints.
These endpoints manage JWT tokens and user sessions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_database, get_current_user
from app.db.schemas import UserCreate, UserResponse, Token, UserLogin
from app.services.auth_service import AuthService
from app.db.models import User

router = APIRouter()
auth_service = AuthService()

@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_database)
):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **password**: Strong password (minimum 6 characters)
    
    Returns the created user information (without password).
    """
    try:
        user = auth_service.create_user(db, user_create)
        return UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

@router.post("/login", response_model=Token)
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_database)
):
    """
    Authenticate user and return JWT token.
    
    - **email**: Registered email address
    - **password**: User password
    
    Returns JWT access token for authenticated requests.
    """
    user = auth_service.authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return auth_service.create_access_token_for_user(user)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header:
    `Authorization: Bearer <your-token>`
    
    Returns current user profile information.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )