"""
SQLAlchemy Database Models

Defines the database schema using SQLAlchemy ORM models.
These models represent our database tables and relationships.
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base

class User(Base):
    """
    User model for authentication and user management.
    """
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")

class Document(Base):
    """
    Document model for uploaded PDF files.
    """
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)  # Path to stored file
    status = Column(String, default="processing")  # processing, ready, error
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    conversations = relationship("ChatConversation", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    """
    Document chunks for RAG processing.
    Stores text chunks and their embeddings for semantic search.
    """
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Text)  # Store vector as JSON string for SQLite compatibility
    metadata_json = Column(Text)  # Store metadata as JSON string
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")

class ChatConversation(Base):
    """
    Chat conversations for question-answering history.
    """
    __tablename__ = "chat_conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    relevant_chunks = Column(Text)  # Store as JSON string
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="conversations")