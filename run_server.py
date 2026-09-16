#!/usr/bin/env python3
"""
Development server runner for AI Business Assistant

This script starts the FastAPI development server with proper configuration.
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting AI Business Assistant Development Server...")
    print("📊 API Documentation will be available at:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("   - Health Check: http://localhost:8000/health")
    print()
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )