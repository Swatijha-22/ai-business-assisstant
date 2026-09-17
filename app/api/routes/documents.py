"""
Document Management API Routes

Handles PDF upload, processing, and document management.
These endpoints manage user documents and trigger AI processing.
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session

from app.api.deps import get_database, get_current_user
from app.db.schemas import DocumentResponse, DocumentUploadResponse, DocumentList
from app.db.models import User, Document
from app.services.document_service import DocumentService

router = APIRouter()
document_service = DocumentService()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Upload and process a PDF document.
    
    - **file**: PDF file to upload (max 10MB)
    - Requires authentication (JWT token)
    - Processes PDF and extracts text for AI processing
    - Returns document ID and processing status
    
    The system will:
    1. Validate file type and size
    2. Store file securely
    3. Extract text from PDF
    4. Split text into chunks for AI processing
    5. Store document metadata in database
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    return await document_service.upload_document(file, current_user.id, db)

@router.get("/", response_model=DocumentList)
async def list_documents(
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of documents to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Get list of user's documents with pagination.
    
    - **skip**: Number of documents to skip (for pagination)
    - **limit**: Maximum documents to return (1-100, default 10)
    - Requires authentication (JWT token)
    - Returns only documents belonging to the authenticated user
    
    Supports pagination for large document collections.
    """
    documents = document_service.get_user_documents(
        current_user.id, db, skip=skip, limit=limit
    )
    
    # Get total count for pagination
    total_count = db.query(Document).filter(Document.user_id == current_user.id).count()
    
    return DocumentList(
        documents=documents,
        total=total_count,
        page=skip // limit + 1,
        page_size=limit
    )

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Get specific document details.
    
    - **document_id**: ID of the document to retrieve
    - Requires authentication (JWT token)
    - Returns document metadata and processing status
    - Only returns documents owned by the authenticated user
    """
    document = document_service.get_document_by_id(document_id, current_user.id, db)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Delete a document and all associated data.
    
    - **document_id**: ID of the document to delete
    - Requires authentication (JWT token)
    - Deletes physical file, database record, and all associated chunks
    - Only allows deletion of documents owned by the authenticated user
    
    **Warning**: This action is irreversible!
    """
    success = document_service.delete_document(document_id, current_user.id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }