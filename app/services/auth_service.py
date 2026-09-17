"""
Authentication Service

Handles user registration, login, and JWT token management.
This service contains the business logic for user authentication.
"""

from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password, verify_password, create_access_token, verify_token
from app.core.config import get_settings
from app.db.models import User
from app.db.schemas import UserCreate, UserResponse, Token

settings = get_settings()

class AuthService:
    """
    Service class for authentication operations.
    
    This class handles:
    - User registration
    - User login and authentication
    - JWT token creation and validation
    """
    
    def create_user(self, db: Session, user_create: UserCreate) -> User:
        """
        Create a new user account.
        
        Args:
            db: Database session
            user_create: User registration data
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_create.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user with hashed password
        hashed_password = hash_password(user_create.password)
        db_user = User(
            email=user_create.email,
            password_hash=hashed_password,
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    def create_access_token_for_user(self, user: User) -> Token:
        """
        Create JWT access token for a user.
        
        Args:
            user: User object
            
        Returns:
            Token response with access token
        """
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.id}, 
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer"
        )
    
    def get_current_user(self, db: Session, token: str) -> User:
        """
        Get current user from JWT token.
        
        Args:
            db: Database session
            token: JWT access token
            
        Returns:
            Current user object
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = verify_token(token)
            if payload is None:
                raise credentials_exception
            
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except Exception:
            raise credentials_exception
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        
        return user
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()