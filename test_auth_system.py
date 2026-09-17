#!/usr/bin/env python3
"""
Authentication System Test

This script tests our authentication system to ensure it's working properly.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_database_creation():
    """Test that we can create database tables"""
    print("📊 Testing database creation...")
    
    try:
        from app.db.database import init_database
        init_database()
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False

def test_user_model():
    """Test that user model works"""
    print("\n👤 Testing user model...")
    
    try:
        from app.db.models import User
        from app.db.database import SessionLocal
        
        # Create a test user
        db = SessionLocal()
        
        test_user = User(
            email="test@example.com",
            password_hash="dummy_hash",
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Verify user was created
        stored_user = db.query(User).filter(User.email == "test@example.com").first()
        if stored_user and stored_user.email == "test@example.com":
            print("✅ User model works correctly")
            
            # Clean up
            db.delete(stored_user)
            db.commit()
            db.close()
            return True
        else:
            db.close()
            print("❌ User model test failed")
            return False
            
    except Exception as e:
        print(f"❌ User model test failed: {e}")
        return False

def test_auth_service():
    """Test authentication service"""
    print("\n🔐 Testing authentication service...")
    
    try:
        from app.services.auth_service import AuthService
        from app.db.schemas import UserCreate
        from app.db.database import SessionLocal
        from app.db.models import User
        
        db = SessionLocal()
        auth_service = AuthService()
        
        # Test user creation
        user_data = UserCreate(email="testauth@example.com", password="testpass123")
        created_user = auth_service.create_user(db, user_data)
        
        if created_user and created_user.email == "testauth@example.com":
            print("✅ User creation works")
            
            # Test authentication
            authenticated_user = auth_service.authenticate_user(
                db, "testauth@example.com", "testpass123"
            )
            
            if authenticated_user:
                print("✅ User authentication works")
                
                # Test token creation
                token = auth_service.create_access_token_for_user(authenticated_user)
                if token.access_token:
                    print("✅ JWT token creation works")
                    
                    # Clean up
                    db.delete(created_user)
                    db.commit()
                    db.close()
                    return True
        
        db.close()
        return False
        
    except Exception as e:
        print(f"❌ Auth service test failed: {e}")
        return False

def test_fastapi_import():
    """Test that FastAPI app can be imported"""
    print("\n🚀 Testing FastAPI app import...")
    
    try:
        from app.main import app
        if app:
            print("✅ FastAPI app imported successfully")
            return True
        else:
            print("❌ FastAPI app import failed")
            return False
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI Business Assistant - Authentication System Test")
    print("=" * 60)
    
    success = True
    success &= test_database_creation()
    success &= test_user_model()
    success &= test_auth_service()
    success &= test_fastapi_import()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Authentication system is ready.")
        print("\n✅ You can now:")
        print("   - Start the server: python run_server.py")
        print("   - Test endpoints at: http://localhost:8000/docs")
        print("   - Register users via API")
        print("   - Login and get JWT tokens")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)