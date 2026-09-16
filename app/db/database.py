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

# Database engine - will be configured when we set up PostgreSQL
engine = None
SessionLocal = None

# SQLAlchemy declarative base for models
Base = declarative_base()

def init_database():
    """
    Initialize database connection.
    This will be implemented when we configure PostgreSQL.
    """
    global engine, SessionLocal
    
    # TODO: Implement when we have database_url configured
    # engine = create_engine(settings.database_url)
    # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    pass

def get_db() -> Generator[Session, None, None]:
    """
    Database dependency that provides a database session.
    
    Yields:
        Database session
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables.
    This will be called during application startup.
    """
    if engine is None:
        raise RuntimeError("Database engine not initialized.")
    
    Base.metadata.create_all(bind=engine)