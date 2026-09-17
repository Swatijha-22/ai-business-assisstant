#!/usr/bin/env python3
"""
Check Document Chunks

Verifies that document processing created text chunks correctly.
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def check_document_processing():
    """Check if documents were processed and chunks created"""
    try:
        from app.db.database import SessionLocal
        from app.db.models import Document, DocumentChunk, User
        
        db = SessionLocal()
        
        print("🔍 Checking document processing results...")
        print("=" * 50)
        
        # Get all documents
        documents = db.query(Document).all()
        print(f"📄 Total documents: {len(documents)}")
        
        for doc in documents:
            print(f"\n📁 Document: {doc.filename}")
            print(f"   ID: {doc.id}")
            print(f"   Status: {doc.status}")
            print(f"   File size: {doc.file_size} bytes")
            print(f"   Created: {doc.created_at}")
            
            # Get chunks for this document
            chunks = db.query(DocumentChunk).filter(
                DocumentChunk.document_id == doc.id
            ).all()
            
            print(f"   Chunks: {len(chunks)}")
            
            for i, chunk in enumerate(chunks):
                preview = chunk.chunk_text[:100] + "..." if len(chunk.chunk_text) > 100 else chunk.chunk_text
                print(f"   Chunk {i+1}: {len(chunk.chunk_text)} chars")
                print(f"      Preview: {preview}")
                print(f"      Metadata: {chunk.metadata_json}")
        
        db.close()
        
        if documents and any(len(db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()) > 0 for doc in documents):
            print("\n✅ Document processing successful!")
            print("   - PDFs uploaded and stored")
            print("   - Text extracted from documents") 
            print("   - Text split into chunks for AI processing")
            return True
        else:
            print("\n⚠️ No processed documents or chunks found")
            return False
        
    except Exception as e:
        print(f"❌ Error checking document processing: {e}")
        return False

if __name__ == "__main__":
    success = check_document_processing()
    if success:
        print("\n🚀 Document processing pipeline is working correctly!")
    else:
        print("\n🔧 Document processing needs attention.")
    sys.exit(0 if success else 1)