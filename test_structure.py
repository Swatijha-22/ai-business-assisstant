#!/usr/bin/env python3
"""
Test script to verify our project structure is correct.
This validates that all imports work and the basic FastAPI app can be created.
"""

def test_imports():
    """Test that all our modules can be imported correctly"""
    print("Testing imports...")
    
    try:
        # Test core imports
        from app.core.config import get_settings
        from app.core.security import hash_password
        print("✅ Core modules imported successfully")
        
        # Test database imports  
        from app.db.models import User, Document
        from app.db.schemas import UserCreate, DocumentResponse
        print("✅ Database modules imported successfully")
        
        # Test service imports
        from app.services.document_service import DocumentService
        from app.services.embedding_service import EmbeddingService  
        from app.services.retrieval_service import RetrievalService
        from app.services.llm_service import LLMService
        print("✅ Service modules imported successfully")
        
        # Test API imports
        from app.api.routes import auth, documents, chat
        print("✅ API route modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_fastapi_basic():
    """Test basic FastAPI app creation"""
    print("\nTesting FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        
        # Create simple app
        app = FastAPI(title="Test App")
        
        @app.get("/")
        def root():
            return {"message": "Hello World"}
            
        print("✅ FastAPI app created successfully")
        return True
        
    except Exception as e:
        print(f"❌ FastAPI error: {e}")
        return False

def test_settings():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        print(f"✅ Settings loaded: {settings.app_name}")
        print(f"   - Version: {settings.app_version}")
        print(f"   - Debug: {settings.debug}")
        return True
        
    except Exception as e:
        print(f"❌ Settings error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AI Business Assistant - Structure Test\n")
    
    success = True
    success &= test_imports()
    success &= test_fastapi_basic() 
    success &= test_settings()
    
    if success:
        print("\n🎉 All tests passed! Project structure is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")