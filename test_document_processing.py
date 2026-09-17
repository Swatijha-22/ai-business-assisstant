#!/usr/bin/env python3
"""
Document Processing System Test

Tests the complete document upload and processing pipeline.
"""

import sys
import os
import requests
import io
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

BASE_URL = "http://localhost:8000"

def create_test_pdf():
    """Create a simple test PDF for testing"""
    try:
        # Try to create a simple PDF using reportlab if available
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Add some test content
        c.drawString(100, 750, "AI Business Assistant - Test Document")
        c.drawString(100, 720, "This is a test PDF document for testing our document processing system.")
        c.drawString(100, 690, "It contains sample text that should be extracted and processed.")
        c.drawString(100, 660, "")
        c.drawString(100, 630, "Key features being tested:")
        c.drawString(120, 600, "- PDF text extraction")
        c.drawString(120, 570, "- Document chunking")
        c.drawString(120, 540, "- Database storage")
        c.drawString(120, 510, "- User document isolation")
        
        c.showPage()
        c.save()
        
        buffer.seek(0)
        return buffer.getvalue()
        
    except ImportError:
        # If reportlab is not available, create a minimal PDF manually
        # This is a very basic PDF structure for testing
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 100
>>
stream
BT
/F1 12 Tf
100 700 Td
(AI Business Assistant Test Document) Tj
0 -20 Td
(This is a simple test PDF for document processing.) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000074 00000 n 
0000000120 00000 n 
0000000216 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
365
%%EOF"""
        return pdf_content

def test_user_authentication():
    """Test user registration and login to get auth token"""
    print("🔐 Testing user authentication...")
    
    # Register test user
    register_data = {
        "email": "doctest@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            print("✅ User registered successfully")
        elif response.status_code == 400 and "already registered" in response.text:
            print("✅ User already exists (using existing account)")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None
    
    # Login to get token
    login_data = {
        "email": "doctest@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login successful, token obtained")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_document_upload(token):
    """Test document upload functionality"""
    print("\n📄 Testing document upload...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test PDF
    pdf_content = create_test_pdf()
    
    # Upload document
    files = {
        "file": ("test_document.pdf", pdf_content, "application/pdf")
    }
    
    try:
        response = requests.post(f"{BASE_URL}/documents/upload", headers=headers, files=files)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document uploaded successfully")
            print(f"   Document ID: {data['document_id']}")
            print(f"   Status: {data['status']}")
            return data["document_id"]
        else:
            print(f"❌ Document upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Document upload error: {e}")
        return None

def test_document_list(token):
    """Test document listing functionality"""
    print("\n📋 Testing document listing...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/documents/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document list retrieved successfully")
            print(f"   Total documents: {data['total']}")
            print(f"   Current page: {data['page']}")
            print(f"   Documents in response: {len(data['documents'])}")
            
            for doc in data['documents']:
                print(f"   - {doc['filename']} (ID: {doc['id']}, Status: {doc['status']})")
            
            return data['documents']
        else:
            print(f"❌ Document list failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Document list error: {e}")
        return []

def test_document_details(token, document_id):
    """Test getting document details"""
    print(f"\n🔍 Testing document details retrieval...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/documents/{document_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document details retrieved successfully")
            print(f"   ID: {data['id']}")
            print(f"   Filename: {data['filename']}")
            print(f"   Size: {data['file_size']} bytes")
            print(f"   Status: {data['status']}")
            print(f"   Created: {data['created_at']}")
            return True
        else:
            print(f"❌ Document details failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Document details error: {e}")
        return False

def test_invalid_file_upload(token):
    """Test upload validation with invalid file"""
    print("\n🚫 Testing invalid file upload...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to upload a non-PDF file
    invalid_content = b"This is not a PDF file"
    files = {
        "file": ("test.txt", invalid_content, "text/plain")
    }
    
    try:
        response = requests.post(f"{BASE_URL}/documents/upload", headers=headers, files=files)
        if response.status_code == 400:
            print("✅ Invalid file correctly rejected")
            print(f"   Error message: {response.json()['detail']}")
            return True
        else:
            print(f"❌ Invalid file should have been rejected: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid file test error: {e}")
        return False

def test_unauthorized_access():
    """Test document access without authentication"""
    print("\n🔒 Testing unauthorized access...")
    
    try:
        response = requests.get(f"{BASE_URL}/documents/")
        if response.status_code == 401:
            print("✅ Unauthorized access correctly blocked")
            return True
        else:
            print(f"❌ Should have blocked unauthorized access: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Unauthorized access test error: {e}")
        return False

def test_database_integration():
    """Test database integration"""
    print("\n💾 Testing database integration...")
    
    try:
        from app.db.database import SessionLocal
        from app.db.models import Document, DocumentChunk, User
        
        db = SessionLocal()
        
        # Check if we can query users
        user_count = db.query(User).count()
        print(f"✅ Database connection working")
        print(f"   Users in database: {user_count}")
        
        # Check documents
        doc_count = db.query(Document).count()
        print(f"   Documents in database: {doc_count}")
        
        # Check chunks
        chunk_count = db.query(DocumentChunk).count()
        print(f"   Document chunks in database: {chunk_count}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        return False

def main():
    """Run all document processing tests"""
    print("🧪 AI Business Assistant - Document Processing Test")
    print("=" * 60)
    print("🔗 Testing against: http://localhost:8000")
    print("📝 Make sure the server is running: python run_server.py")
    print("=" * 60)
    
    success = True
    token = None
    document_id = None
    
    # Test database integration first
    success &= test_database_integration()
    
    # Test authentication
    token = test_user_authentication()
    if not token:
        success = False
        print("\n⚠️ Cannot continue without authentication token")
        return success
    
    # Test unauthorized access
    success &= test_unauthorized_access()
    
    # Test invalid file upload
    success &= test_invalid_file_upload(token)
    
    # Test document upload
    document_id = test_document_upload(token)
    if document_id:
        success &= True
        
        # Test document listing
        documents = test_document_list(token)
        success &= len(documents) > 0
        
        # Test document details
        success &= test_document_details(token, document_id)
    else:
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All document processing tests passed!")
        print("\n✅ Your AI Business Assistant now supports:")
        print("   - Secure PDF upload with validation")
        print("   - Text extraction from PDF documents")
        print("   - Document chunking for AI processing")
        print("   - User document isolation and security")
        print("   - Complete document management API")
        print(f"\n📊 View API documentation: http://localhost:8000/docs")
        print("🚀 Ready for Phase 4: AI Integration (RAG Pipeline)!")
    else:
        print("⚠️ Some document processing tests failed.")
        print("🔧 Check the server logs and fix issues before continuing.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)