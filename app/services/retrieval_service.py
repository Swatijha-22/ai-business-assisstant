"""
Retrieval Service

Handles semantic search and context retrieval for RAG pipeline.
Coordinates between embedding service and database for efficient vector search.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.services.embedding_service import EmbeddingService
from app.db.models import DocumentChunk, Document
from app.core.config import get_settings

settings = get_settings()

class RetrievalService:
    """
    Service class for semantic retrieval operations.
    
    This class handles:
    - Question embedding generation
    - Semantic search across document chunks
    - Context preparation for LLM
    - Relevance scoring and ranking
    """
    
    def __init__(self):
        """Initialize retrieval service"""
        self.embedding_service = EmbeddingService()
        self.default_top_k = 5
        self.similarity_threshold = 0.3
    
    async def retrieve_relevant_chunks(
        self, 
        question: str, 
        document_id: str, 
        db: Session,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant document chunks for a question.
        
        Pipeline:
        1. Generate embedding for the question
        2. Get all chunks for the document from database
        3. Calculate similarities and rank chunks
        4. Return top-k most relevant chunks with metadata
        
        Args:
            question: User question
            document_id: ID of the document to search
            db: Database session
            top_k: Number of chunks to retrieve (defaults to 5)
            
        Returns:
            List of relevant chunks with similarity scores and metadata
        """
        if top_k is None:
            top_k = self.default_top_k
        
        try:
            print(f"🔍 Retrieving relevant chunks for question: '{question[:50]}...'")
            
            # Step 1: Generate embedding for the question
            question_embedding = self.embedding_service.generate_embedding(question)
            print(f"✅ Generated question embedding (dimension: {len(question_embedding)})")
            
            # Step 2: Get all chunks for this document
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).order_by(DocumentChunk.chunk_index).all()
            
            if not chunks:
                print("⚠️ No chunks found for document")
                return []
            
            print(f"📄 Found {len(chunks)} chunks to search")
            
            # Step 3: Calculate similarities
            chunk_similarities = []
            
            for chunk in chunks:
                try:
                    # Get chunk embedding (convert from JSON storage)
                    if chunk.embedding:
                        chunk_embedding = self.embedding_service.json_to_embedding(chunk.embedding)
                        
                        # Calculate similarity
                        similarity = self.embedding_service.calculate_similarity(
                            question_embedding, chunk_embedding
                        )
                        
                        # Parse metadata
                        metadata = json.loads(chunk.metadata_json) if chunk.metadata_json else {}
                        
                        chunk_similarities.append({
                            'chunk_id': chunk.id,
                            'chunk_text': chunk.chunk_text,
                            'chunk_index': chunk.chunk_index,
                            'similarity_score': similarity,
                            'metadata': metadata
                        })
                        
                except Exception as e:
                    print(f"⚠️ Error processing chunk {chunk.id}: {e}")
                    continue
            
            # Step 4: Sort by similarity and return top-k
            chunk_similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            relevant_chunks = chunk_similarities[:top_k]
            
            # Filter by similarity threshold
            relevant_chunks = [
                chunk for chunk in relevant_chunks 
                if chunk['similarity_score'] >= self.similarity_threshold
            ]
            
            print(f"✅ Retrieved {len(relevant_chunks)} relevant chunks")
            for i, chunk in enumerate(relevant_chunks):
                print(f"   Chunk {i+1}: similarity={chunk['similarity_score']:.3f}")
            
            return relevant_chunks
            
        except Exception as e:
            print(f"❌ Error retrieving chunks: {e}")
            raise RuntimeError(f"Failed to retrieve relevant chunks: {e}")
    
    async def retrieve_from_all_user_documents(
        self,
        question: str,
        user_id: str,
        db: Session,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks from all user documents.
        
        This allows questions that span multiple documents.
        
        Args:
            question: User question
            user_id: User ID to limit search scope
            db: Database session
            top_k: Number of chunks to retrieve
            
        Returns:
            List of relevant chunks with document context
        """
        if top_k is None:
            top_k = self.default_top_k
        
        try:
            print(f"🔍 Searching across all user documents for: '{question[:50]}...'")
            
            # Generate question embedding
            question_embedding = self.embedding_service.generate_embedding(question)
            
            # Get all chunks from user's documents
            chunks = db.query(DocumentChunk).join(Document).filter(
                Document.user_id == user_id
            ).all()
            
            if not chunks:
                print("⚠️ No chunks found for user")
                return []
            
            print(f"📄 Searching {len(chunks)} chunks across user's documents")
            
            # Calculate similarities
            chunk_similarities = []
            
            for chunk in chunks:
                try:
                    if chunk.embedding:
                        chunk_embedding = self.embedding_service.json_to_embedding(chunk.embedding)
                        similarity = self.embedding_service.calculate_similarity(
                            question_embedding, chunk_embedding
                        )
                        
                        metadata = json.loads(chunk.metadata_json) if chunk.metadata_json else {}
                        
                        chunk_similarities.append({
                            'chunk_id': chunk.id,
                            'chunk_text': chunk.chunk_text,
                            'chunk_index': chunk.chunk_index,
                            'document_id': chunk.document_id,
                            'document_filename': chunk.document.filename,
                            'similarity_score': similarity,
                            'metadata': metadata
                        })
                        
                except Exception as e:
                    continue
            
            # Sort and filter
            chunk_similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            relevant_chunks = chunk_similarities[:top_k]
            relevant_chunks = [
                chunk for chunk in relevant_chunks 
                if chunk['similarity_score'] >= self.similarity_threshold
            ]
            
            print(f"✅ Retrieved {len(relevant_chunks)} relevant chunks from multiple documents")
            
            return relevant_chunks
            
        except Exception as e:
            print(f"❌ Error retrieving from user documents: {e}")
            raise RuntimeError(f"Failed to retrieve from user documents: {e}")
    
    def prepare_context_for_llm(self, relevant_chunks: List[Dict[str, Any]]) -> str:
        """
        Prepare context string from retrieved chunks for LLM input.
        
        Formats the retrieved chunks into a coherent context that provides
        the LLM with relevant information to answer the question.
        
        Args:
            relevant_chunks: List of relevant chunks with metadata
            
        Returns:
            Formatted context string for LLM
        """
        if not relevant_chunks:
            return "No relevant context found in the documents."
        
        context_parts = []
        
        for i, chunk in enumerate(relevant_chunks, 1):
            # Format each chunk with relevance info
            chunk_context = f"[Context {i}] (Relevance: {chunk['similarity_score']:.2f})\n"
            
            # Add document info if available
            if 'document_filename' in chunk:
                chunk_context += f"From document: {chunk['document_filename']}\n"
            
            # Add the actual chunk text
            chunk_context += f"{chunk['chunk_text']}\n"
            
            context_parts.append(chunk_context)
        
        # Join all contexts with separators
        full_context = "\n" + "="*50 + "\n".join(context_parts)
        
        return full_context
    
    def calculate_retrieval_confidence(self, relevant_chunks: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence score for the retrieval results.
        
        Uses similarity scores and other factors to estimate how well
        the retrieved context can answer the question.
        
        Args:
            relevant_chunks: Retrieved chunks with similarity scores
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not relevant_chunks:
            return 0.0
        
        # Get similarity scores
        similarities = [chunk['similarity_score'] for chunk in relevant_chunks]
        
        # Calculate weighted confidence based on top similarities
        if len(similarities) >= 3:
            # If we have 3+ chunks, use weighted average
            weights = [0.5, 0.3, 0.2]  # Give more weight to top chunks
            confidence = sum(sim * weight for sim, weight in zip(similarities[:3], weights))
        elif len(similarities) == 2:
            # If we have 2 chunks, weight them
            confidence = similarities[0] * 0.7 + similarities[1] * 0.3
        else:
            # If we have 1 chunk, use its similarity
            confidence = similarities[0]
        
        # Apply confidence thresholds
        if confidence >= 0.8:
            return min(confidence, 0.95)  # High confidence
        elif confidence >= 0.6:
            return confidence * 0.85      # Good confidence
        elif confidence >= 0.4:
            return confidence * 0.7       # Moderate confidence
        else:
            return confidence * 0.5       # Low confidence
        
    def get_retrieval_stats(self, relevant_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the retrieval results.
        
        Args:
            relevant_chunks: Retrieved chunks
            
        Returns:
            Dictionary with retrieval statistics
        """
        if not relevant_chunks:
            return {
                'num_chunks': 0,
                'avg_similarity': 0.0,
                'max_similarity': 0.0,
                'min_similarity': 0.0,
                'confidence': 0.0
            }
        
        similarities = [chunk['similarity_score'] for chunk in relevant_chunks]
        
        return {
            'num_chunks': len(relevant_chunks),
            'avg_similarity': sum(similarities) / len(similarities),
            'max_similarity': max(similarities),
            'min_similarity': min(similarities),
            'confidence': self.calculate_retrieval_confidence(relevant_chunks),
            'chunks_above_threshold': len([s for s in similarities if s >= self.similarity_threshold])
        }