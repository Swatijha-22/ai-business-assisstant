"""
Document Processing Service

Handles PDF upload, text extraction, and document management business logic.
This service orchestrates the document processing pipeline.
"""

import os
import uuid
import aiofiles
import fitz  # PyMuPDF
from typing import List, Optional, BinaryIO
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Document, User, DocumentChunk
from app.db.schemas import DocumentResponse, DocumentUploadResponse

settings = get_settings()

class DocumentService:
    """
    Service class for document processing operations.
    
    This class handles:
    - File validation and storage
    - PDF text extraction 
    - Document chunking
    - Document management and retrieval
    """
    
    def __init__(self):
        """Initialize document service"""
        self.upload_dir = Path(settings.upload_directory)
        self.upload_dir.mkdir(exist_ok=True)
        self.max_file_size = settings.max_file_size
        self.allowed_extensions = settings.allowed_file_types
    
    async def upload_document(self, file: UploadFile, user_id: str, db: Session) -> DocumentUploadResponse:
        """
        Process uploaded document.
        
        Pipeline:
        1. Validate file (type, size, content)
        2. Store file securely
        3. Extract text from PDF
        4. Create database record
        5. Process text into chunks
        
        Args:
            file: Uploaded file from FastAPI
            user_id: ID of the user uploading the file
            db: Database session
            
        Returns:
            Document upload response with status
        """
        try:
            # Step 1: Validate file
            await self._validate_file(file)
            
            # Step 2: Generate unique filename and store file
            file_id = str(uuid.uuid4())
            file_extension = self._get_file_extension(file.filename)
            stored_filename = f"{file_id}{file_extension}"
            file_path = self.upload_dir / stored_filename
            
            # Save file to disk
            await self._save_file(file, file_path)
            
            # Step 3: Create database record
            document = Document(
                id=file_id,
                user_id=user_id,
                filename=file.filename,
                file_size=file.size if file.size else 0,
                file_path=str(file_path),
                status="processing"
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            # Step 4: Process PDF in background (for now, immediately)
            try:
                await self._process_pdf(document, db)
                document.status = "ready"
            except Exception as e:
                document.status = "error"
                print(f"PDF processing error: {e}")
            
            db.commit()
            
            return DocumentUploadResponse(
                message="Document uploaded and processed successfully",
                document_id=document.id,
                status=document.status
            )
            
        except HTTPException:
            raise
        except Exception as e:
            # Clean up file if database operation fails
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document upload failed: {str(e)}"
            )
    
    async def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.
        
        Checks:
        - File type (PDF only)
        - File size limits
        - File content validation
        
        Args:
            file: Uploaded file to validate
            
        Raises:
            HTTPException: If validation fails
        """
        # Check file extension
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )
        
        file_extension = self._get_file_extension(file.filename)
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not allowed. Only PDF files are supported."
            )
        
        # Check file size
        if file.size and file.size > self.max_file_size:
            max_size_mb = self.max_file_size / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {max_size_mb:.1f}MB"
            )
        
        # Reset file position for reading
        await file.seek(0)
        
        # Basic PDF validation - check PDF header
        header = await file.read(8)
        await file.seek(0)
        
        if not header.startswith(b'%PDF-'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file format"
            )
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        return Path(filename).suffix.lower()
    
    async def _save_file(self, file: UploadFile, file_path: Path) -> None:
        """
        Save uploaded file to disk.
        
        Args:
            file: FastAPI uploaded file
            file_path: Path where to save the file
        """
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    
    async def _process_pdf(self, document: Document, db: Session) -> None:
        """
        Process PDF file - extract text, create chunks, and generate embeddings.
        
        Args:
            document: Document database record
            db: Database session
        """
        # Extract text from PDF
        text_content = await self._extract_text_from_pdf(document.file_path)
        
        if not text_content.strip():
            raise Exception("No text could be extracted from PDF")
        
        # Create text chunks
        chunks = self._chunk_text(text_content)
        
        if not chunks:
            raise Exception("No chunks could be created from extracted text")
        
        print(f"📄 Created {len(chunks)} text chunks from PDF")
        
        # Generate embeddings for chunks
        from app.services.embedding_service import EmbeddingService
        embedding_service = EmbeddingService()
        
        try:
            # Extract chunk texts for batch embedding generation
            chunk_texts = [chunk['text'] for chunk in chunks]
            embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
            
            print(f"🔮 Generated {len(embeddings)} embeddings")
            
            # Store chunks with embeddings in database
            for idx, (chunk_data, embedding) in enumerate(zip(chunks, embeddings)):
                # Convert embedding to JSON for storage
                embedding_json = embedding_service.embedding_to_json(embedding)
                
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_text=chunk_data['text'],
                    chunk_index=idx,
                    embedding=embedding_json,
                    metadata_json=str(chunk_data.get('metadata', {}))
                )
                db.add(chunk)
            
            db.commit()
            print(f"✅ Stored {len(chunks)} chunks with embeddings in database")
            
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            # Still store chunks without embeddings so document isn't lost
            for idx, chunk_data in enumerate(chunks):
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_text=chunk_data['text'],
                    chunk_index=idx,
                    embedding=None,  # No embedding due to error
                    metadata_json=str(chunk_data.get('metadata', {}))
                )
                db.add(chunk)
            
            db.commit()
            print(f"⚠️ Stored {len(chunks)} chunks without embeddings due to error")
            raise Exception(f"Failed to generate embeddings: {e}")
    
    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file using PyMuPDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            doc = fitz.open(file_path)
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                text_content += f"\n--- Page {page_num + 1} ---\n{text}\n"
            
            doc.close()
            return text_content
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[dict]:
        """
        Split text into chunks for processing.
        
        Strategy:
        - Fixed-size chunks with overlap
        - Preserve sentence boundaries where possible
        - Include metadata (page info, chunk index)
        
        Args:
            text: Full document text
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of text chunks with metadata
        """
        if not text.strip():
            return []
        
        chunks = []
        words = text.split()
        current_chunk = ""
        current_word_count = 0
        
        for word in words:
            # Check if adding this word would exceed chunk size
            test_chunk = current_chunk + " " + word if current_chunk else word
            
            if len(test_chunk) > chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': {
                        'word_count': current_word_count,
                        'char_count': len(current_chunk)
                    }
                })
                
                # Start new chunk with overlap
                overlap_words = current_chunk.split()[-overlap//10:]  # Rough word overlap
                current_chunk = " ".join(overlap_words) + " " + word
                current_word_count = len(overlap_words) + 1
            else:
                current_chunk = test_chunk
                current_word_count += 1
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': {
                    'word_count': current_word_count,
                    'char_count': len(current_chunk)
                }
            })
        
        return chunks
    
    def get_user_documents(self, user_id: str, db: Session, skip: int = 0, limit: int = 10) -> List[DocumentResponse]:
        """
        Get documents for a user with pagination.
        
        Args:
            user_id: User ID
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of user's documents
        """
        documents = db.query(Document).filter(
            Document.user_id == user_id
        ).offset(skip).limit(limit).all()
        
        return [
            DocumentResponse(
                id=doc.id,
                filename=doc.filename,
                file_size=doc.file_size,
                status=doc.status,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            )
            for doc in documents
        ]
    
    def get_document_by_id(self, document_id: str, user_id: str, db: Session) -> Optional[DocumentResponse]:
        """
        Get specific document by ID with user ownership check.
        
        Args:
            document_id: Document ID
            user_id: User ID for ownership validation
            db: Database session
            
        Returns:
            Document data or None if not found/unauthorized
        """
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
        
        if not document:
            return None
        
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            file_size=document.file_size,
            status=document.status,
            created_at=document.created_at,
            updated_at=document.updated_at
        )
    
    def delete_document(self, document_id: str, user_id: str, db: Session) -> bool:
        """
        Delete document and all associated data.
        
        Args:
            document_id: Document ID
            user_id: User ID for ownership validation
            db: Database session
            
        Returns:
            True if successful, False if not found
        """
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
        
        if not document:
            return False
        
        try:
            # Delete physical file
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Delete from database (cascades to chunks and conversations)
            db.delete(document)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error deleting document: {e}")
            return False