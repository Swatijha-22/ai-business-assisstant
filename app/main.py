"""
AI Business Assistant - Main FastAPI Application

This is the entry point for our AI-powered document and data automation platform.
Version 1: AI Document Assistant with authentication and PDF Q&A capabilities.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth
from app.db.database import init_database

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="AI Business Assistant",
        description="Document, Data & Workflow Automation Platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS middleware for frontend integration (later phases)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        """Health check endpoint"""
        return {
            "message": "AI Business Assistant API", 
            "version": "1.0.0",
            "status": "active"
        }

    @app.get("/health")
    async def health_check():
        """Detailed health check for monitoring"""
        return {
            "status": "healthy",
            "service": "ai-business-assistant",
            "version": "1.0.0"
        }

    # Include API routes
    app.include_router(auth.router, prefix="/auth", tags=["authentication"])
    # app.include_router(documents.router, prefix="/documents", tags=["documents"]) 
    # app.include_router(chat.router, prefix="/chat", tags=["chat"])
    
    return app

# Create the app instance
app = create_app()

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    print("🚀 Starting AI Business Assistant...")
    init_database()
    print("✅ Application startup complete")

@app.on_event("shutdown") 
async def shutdown_event():
    """Clean up on application shutdown"""
    print("👋 Shutting down AI Business Assistant...")