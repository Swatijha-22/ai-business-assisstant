"""
Embedding Service

Handles text embedding generation and vector operations for semantic search.
Uses sentence-transformers for local embedding generation without API costs.
"""

import json
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import get_settings

settings = get_settings()

class EmbeddingService:
    """
    Service class for embedding operations.
    
    This class handles:
    - Text embedding generation using sentence-transformers
    - Vector similarity calculations
    - Model management and caching
    - Batch processing for efficiency
    """
    
    def __init__(self):
        """Initialize embedding service"""
        self._model = None
        self.model_name = settings.embedding_model
        self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
    
    def _load_model(self) -> SentenceTransformer:
        """
        Load the sentence transformer model with lazy loading.
        
        Lazy loading prevents model loading during application startup,
        which would slow down the server start time.
        
        Returns:
            Loaded sentence transformer model
        """
        if self._model is None:
            print(f"🤖 Loading embedding model: {self.model_name}")
            try:
                self._model = SentenceTransformer(self.model_name)
                print(f"✅ Embedding model loaded successfully")
                print(f"   Model: {self.model_name}")
                print(f"   Embedding dimension: {self.embedding_dimension}")
            except Exception as e:
                print(f"❌ Failed to load embedding model: {e}")
                raise RuntimeError(f"Could not load embedding model: {e}")
        
        return self._model
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as numpy array
            
        Raises:
            ValueError: If text is empty
            RuntimeError: If model loading fails
        """
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")
        
        model = self._load_model()
        
        try:
            # Generate embedding and ensure it's a numpy array
            embedding = model.encode(text, convert_to_numpy=True)
            
            # Normalize the embedding for better similarity calculations
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate embedding: {e}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Batch processing is more efficient than individual calls
        when processing many texts at once.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            ValueError: If texts list is empty
            RuntimeError: If batch processing fails
        """
        if not texts:
            raise ValueError("Cannot process empty text list")
        
        # Filter out empty texts but keep track of indices
        valid_texts = []
        valid_indices = []
        
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)
        
        if not valid_texts:
            raise ValueError("No valid texts to process")
        
        model = self._load_model()
        
        try:
            print(f"🔄 Generating embeddings for {len(valid_texts)} text chunks...")
            
            # Generate embeddings in batch for efficiency
            embeddings = model.encode(valid_texts, convert_to_numpy=True, show_progress_bar=True)
            
            # Normalize embeddings
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / norms
            
            # Create result array with proper indexing
            result = [None] * len(texts)
            for i, embedding in enumerate(embeddings):
                result[valid_indices[i]] = embedding
            
            print(f"✅ Generated {len(valid_texts)} embeddings successfully")
            return [emb for emb in result if emb is not None]
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate batch embeddings: {e}")
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Cosine similarity is ideal for normalized embeddings and measures
        the angle between vectors, focusing on direction rather than magnitude.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1, where 1 is identical)
            
        Raises:
            ValueError: If embeddings have different shapes or are invalid
        """
        try:
            # Validate inputs
            if embedding1.shape != embedding2.shape:
                raise ValueError("Embeddings must have the same shape")
            
            if len(embedding1.shape) != 1:
                raise ValueError("Embeddings must be 1-dimensional")
            
            # Calculate cosine similarity
            # Using numpy dot product for normalized vectors
            similarity = np.dot(embedding1, embedding2)
            
            # Clamp to [0, 1] range to handle floating point precision issues
            similarity = max(0.0, min(1.0, float(similarity)))
            
            return similarity
            
        except Exception as e:
            raise ValueError(f"Failed to calculate similarity: {e}")
    
    def find_most_similar(
        self, 
        query_embedding: np.ndarray, 
        candidate_embeddings: List[np.ndarray],
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find most similar embeddings to a query embedding.
        
        Uses efficient vectorized operations for fast similarity computation.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity (descending)
            
        Raises:
            ValueError: If inputs are invalid
        """
        if not candidate_embeddings:
            return []
        
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        
        try:
            # Stack embeddings for efficient computation
            candidates_matrix = np.vstack(candidate_embeddings)
            
            # Calculate similarities using matrix multiplication
            similarities = np.dot(candidates_matrix, query_embedding)
            
            # Get top-k indices
            top_k = min(top_k, len(similarities))
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Return (index, similarity) pairs
            results = [(int(idx), float(similarities[idx])) for idx in top_indices]
            
            return results
            
        except Exception as e:
            raise RuntimeError(f"Failed to find similar embeddings: {e}")
    
    def embedding_to_bytes(self, embedding: np.ndarray) -> bytes:
        """
        Convert embedding to bytes for database storage.
        
        Args:
            embedding: Numpy array embedding
            
        Returns:
            Embedding as bytes
        """
        return embedding.astype(np.float32).tobytes()
    
    def bytes_to_embedding(self, embedding_bytes: bytes) -> np.ndarray:
        """
        Convert bytes back to embedding array.
        
        Args:
            embedding_bytes: Embedding stored as bytes
            
        Returns:
            Numpy array embedding
        """
        return np.frombuffer(embedding_bytes, dtype=np.float32)
    
    def embedding_to_json(self, embedding: np.ndarray) -> str:
        """
        Convert embedding to JSON string for database storage (alternative method).
        
        Args:
            embedding: Numpy array embedding
            
        Returns:
            Embedding as JSON string
        """
        return json.dumps(embedding.tolist())
    
    def json_to_embedding(self, embedding_json: str) -> np.ndarray:
        """
        Convert JSON string back to embedding array.
        
        Args:
            embedding_json: Embedding stored as JSON string
            
        Returns:
            Numpy array embedding
        """
        return np.array(json.loads(embedding_json), dtype=np.float32)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current embedding model.
        
        Returns:
            Dictionary with model information
        """
        model = self._load_model()
        
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "max_sequence_length": getattr(model, 'max_seq_length', 'Unknown'),
            "is_loaded": self._model is not None
        }