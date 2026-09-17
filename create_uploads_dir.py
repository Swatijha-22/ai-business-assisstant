#!/usr/bin/env python3
"""
Upload Directory Setup

Creates the necessary directory structure for file uploads.
"""

import os
from pathlib import Path

def create_upload_directories():
    """Create upload directories if they don't exist"""
    
    # Create main uploads directory
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    print(f"✅ Created uploads directory: {uploads_dir.absolute()}")
    
    # Create subdirectories for organization (future use)
    subdirs = ["documents", "temp"]
    for subdir in subdirs:
        subdir_path = uploads_dir / subdir
        subdir_path.mkdir(exist_ok=True)
        print(f"✅ Created subdirectory: {subdir_path}")
    
    # Create .gitkeep files to ensure directories are tracked by git
    gitkeep_files = [
        uploads_dir / ".gitkeep",
        uploads_dir / "documents" / ".gitkeep",
        uploads_dir / "temp" / ".gitkeep"
    ]
    
    for gitkeep in gitkeep_files:
        gitkeep.touch()
        print(f"✅ Created .gitkeep: {gitkeep}")
    
    print("\n🎉 Upload directory structure created successfully!")
    print(f"📁 Main directory: {uploads_dir.absolute()}")
    print("📝 Note: Upload files will be stored here during development")

if __name__ == "__main__":
    create_upload_directories()