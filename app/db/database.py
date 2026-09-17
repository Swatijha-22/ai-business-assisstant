"""
Database Connection and Session Management

Handles SQLAlchemy database connection, session creation, and database initialization.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy declarative base for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Database dependency that provides a database session.
    
    This function will be used as a FastAPI dependency to inject
    database sessions into our API endpoints.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    Initialize database connection and create tables.
    This will be called during application startup.
    """
    # Import models to ensure they are registered with SQLAlchemy
    from app.db import models
    
    # Create all database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def create_tables():
    """
    Create all database tables.
    This will be called during application startup.
    """
    Base.metadata.create_all(bind=engine)