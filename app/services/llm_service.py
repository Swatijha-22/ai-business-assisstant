"""
LLM Service

Handles Large Language Model interactions for answer generation.
Abstracts LLM provider (OpenAI, etc.) behind a service interface for easy switching.
"""

import openai
from typing import Dict, Any, Optional
from app.core.config import get_settings

settings = get_settings()

class LLMService:
    """
    Service class for LLM operations.
    
    This class handles:
    - LLM provider configuration
    - Prompt engineering for RAG
    - Answer generation
    - Response formatting and validation
    """
    
    def __init__(self):
        """Initialize LLM service"""
        self.api_key = settings.openai_api_key
        self.model = "gpt-3.5-turbo"  # Fast and cost-effective model
        self.max_tokens = 500
        self.temperature = 0.1  # Low temperature for factual responses
        
        # Configure OpenAI
        if self.api_key:
            openai.api_key = self.api_key
        else:
            print("⚠️ OpenAI API key not configured. LLM features will use mock responses.")
    
    async def generate_answer(
        self, 
        question: str, 
        context: str, 
        confidence_score: float,
        document_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an answer using the LLM based on question and context.
        
        Args:
            question: User question
            context: Retrieved context from documents
            confidence_score: Confidence in the retrieval quality
            document_filename: Name of the source document (optional)
            
        Returns:
            Generated answer with metadata
        """
        try:
            # Build the RAG prompt
            prompt = self._build_rag_prompt(question, context, confidence_score, document_filename)
            
            # Generate response
            if self.api_key:
                response_data = await self._call_openai_api(prompt)
            else:
                response_data = self._generate_mock_response(question, context, confidence_score)
            
            return response_data
            
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return {
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "model_used": self.model,
                "error": str(e),
                "confidence": 0.0
            }
    
    def _build_rag_prompt(
        self, 
        question: str, 
        context: str, 
        confidence_score: float,
        document_filename: Optional[str] = None
    ) -> str:
        """
        Build the RAG prompt for the LLM.
        
        Creates a structured prompt that instructs the LLM to:
        1. Use only the provided context
        2. Answer based on the document content
        3. Admit when information is insufficient
        4. Be concise and direct
        
        Args:
            question: User question
            context: Retrieved document context
            confidence_score: Retrieval confidence score
            document_filename: Source document name
            
        Returns:
            Formatted prompt string
        """
        # Base RAG prompt template
        base_prompt = """You are an AI assistant that answers questions based on provided document content.

INSTRUCTIONS:
1. Answer the question using ONLY the information provided in the context below.
2. If the context doesn't contain enough information to answer completely, say so clearly.
3. Do not make up or infer information that isn't explicitly stated in the context.
4. Be concise and direct in your responses.
5. If you cannot answer the question from the context, explain what information would be needed.

"""
        
        # Add document context if available
        if document_filename:
            base_prompt += f"DOCUMENT: {document_filename}\n\n"
        
        # Add confidence-based instructions
        if confidence_score < 0.5:
            base_prompt += "NOTE: The retrieved context has low confidence. Be extra careful to only use information that is clearly stated.\n\n"
        elif confidence_score < 0.7:
            base_prompt += "NOTE: The retrieved context has moderate confidence. Focus on information that is clearly relevant.\n\n"
        
        # Add the context and question
        base_prompt += f"CONTEXT:\n{context}\n\n"
        base_prompt += f"QUESTION: {question}\n\n"
        base_prompt += "ANSWER:"
        
        return base_prompt
    
    async def _call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """
        Make API call to OpenAI.
        
        Args:
            prompt: Formatted prompt string
            
        Returns:
            Response data with answer and metadata
        """
        try:
            print(f"🤖 Calling OpenAI API with model: {self.model}")
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful AI assistant that answers questions based on provided document content. Be accurate and concise."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content.strip()
            
            print(f"✅ Generated answer ({len(answer)} characters)")
            
            return {
                "answer": answer,
                "model_used": self.model,
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            raise RuntimeError(f"Failed to call OpenAI API: {e}")
    
    def _generate_mock_response(
        self, 
        question: str, 
        context: str, 
        confidence_score: float
    ) -> Dict[str, Any]:
        """
        Generate a mock response when OpenAI API is not available.
        
        This allows the system to function without API keys for development/testing.
        
        Args:
            question: User question
            context: Retrieved context
            confidence_score: Retrieval confidence
            
        Returns:
            Mock response data
        """
        print("🤖 Using mock LLM response (OpenAI API key not configured)")
        
        # Create a simple mock response based on context
        if "no relevant context found" in context.lower():
            mock_answer = "I don't have enough information in the provided document to answer your question. Could you try rephrasing your question or provide more specific details?"
        elif confidence_score < 0.5:
            mock_answer = f"Based on the document content, I found some information related to your question about '{question[:30]}...', but I don't have enough context to provide a complete answer. The available information suggests some relevant details, but more specific information would be needed for a comprehensive response."
        else:
            # Extract a relevant snippet from context
            context_lines = context.split('\n')
            relevant_line = next((line for line in context_lines if len(line.strip()) > 20), "")
            
            mock_answer = f"Based on the document, I can provide some information about your question. {relevant_line[:100]}... However, please note this is a mock response since the OpenAI API is not configured. For actual AI-powered answers, please configure your OpenAI API key in the environment variables."
        
        return {
            "answer": mock_answer,
            "model_used": "mock-llm",
            "tokens_used": len(mock_answer.split()),
            "confidence": confidence_score,
            "is_mock": True
        }
    
    def validate_response(self, response: str, context: str) -> Dict[str, Any]:
        """
        Validate that the response is appropriate and grounded in context.
        
        Performs basic checks to ensure response quality and groundedness.
        
        Args:
            response: Generated response
            context: Source context
            
        Returns:
            Validation results
        """
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "score": 1.0
        }
        
        # Check response length
        if len(response.strip()) == 0:
            validation_results["is_valid"] = False
            validation_results["warnings"].append("Empty response")
            return validation_results
        
        if len(response) < 10:
            validation_results["warnings"].append("Very short response")
            validation_results["score"] -= 0.2
        
        # Check for common hallucination indicators
        hallucination_phrases = [
            "based on my knowledge",
            "from what i understand",
            "typically",
            "usually", 
            "in general",
            "commonly",
            "often"
        ]
        
        response_lower = response.lower()
        found_phrases = [phrase for phrase in hallucination_phrases if phrase in response_lower]
        
        if found_phrases:
            validation_results["warnings"].append(f"Potential hallucination indicators: {found_phrases}")
            validation_results["score"] -= len(found_phrases) * 0.1
        
        # Check if response acknowledges limitations
        limitation_phrases = [
            "don't have enough information",
            "cannot answer",
            "insufficient information",
            "not enough context",
            "would need more information"
        ]
        
        has_limitations = any(phrase in response_lower for phrase in limitation_phrases)
        if has_limitations and "no relevant context found" not in context.lower():
            validation_results["warnings"].append("Response claims insufficient information despite available context")
            validation_results["score"] -= 0.3
        
        # Normalize score
        validation_results["score"] = max(0.0, min(1.0, validation_results["score"]))
        
        return validation_results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current LLM configuration.
        
        Returns:
            Dictionary with model configuration info
        """
        return {
            "model_name": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "api_configured": bool(self.api_key),
            "provider": "OpenAI"
        }