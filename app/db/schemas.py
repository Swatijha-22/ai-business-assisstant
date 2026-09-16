"""
Pydantic Schemas for Request/Response Validation

Defines the API contract using Pydantic models for request validation
and response serialization. These schemas ensure type safety and API documentation.
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

# ============================================================================
# Authentication Schemas
# ============================================================================

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schema for user information response"""
    id: UUID
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[UUID] = None

# ============================================================================
# Document Schemas
# ============================================================================

class DocumentResponse(BaseModel):
    """Schema for document information response"""
    id: UUID
    filename: str
    file_size: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class DocumentList(BaseModel):
    """Schema for paginated document list response"""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int

class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    message: str
    document_id: UUID
    status: str

# ============================================================================
# Chat Schemas
# ============================================================================

class ChatRequest(BaseModel):
    """Schema for chat question request"""
    question: str

class ChatResponse(BaseModel):
    """Schema for chat answer response"""
    question: str
    answer: str
    relevant_chunks: List[Dict[str, Any]]
    confidence: Optional[float] = None
    
class ChatHistory(BaseModel):
    """Schema for chat conversation history"""
    id: UUID
    question: str
    answer: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatHistoryList(BaseModel):
    """Schema for chat history list response"""
    conversations: List[ChatHistory]
    total: int
    document_id: UUID

# ============================================================================
# Generic Response Schemas
# ============================================================================

class StatusResponse(BaseModel):
    """Generic status response schema"""
    message: str
    status: str

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None