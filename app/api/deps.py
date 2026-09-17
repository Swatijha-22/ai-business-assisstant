"""
Dependency Injection for FastAPI

This module contains reusable dependencies that can be injected into our API endpoints.
Dependencies handle common tasks like authentication, database connections, etc.
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.services.auth_service import AuthService

# JWT token dependency
security = HTTPBearer()

# Auth service instance
auth_service = AuthService()

def get_database() -> Generator[Session, None, None]:
    """
    Database dependency that provides a database session to endpoints.
    """
    yield from get_db()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> User:
    """
    Authentication dependency that extracts and validates the current user.
    
    Args:
        credentials: HTTP authorization credentials (JWT token)
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    user = auth_service.get_current_user(db, token)
    return user