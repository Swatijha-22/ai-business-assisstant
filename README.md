# AI Business Assistant

A production-grade AI-powered platform for document processing, data analysis, and workflow automation.

## Version 1: AI Document Assistant

This initial version provides secure PDF upload, processing, and intelligent question-answering using RAG (Retrieval-Augmented Generation).

### Features

- **User Authentication**: Secure registration and JWT-based authentication
- **Document Management**: PDF upload, processing, and storage
- **AI-Powered Q&A**: Ask questions about uploaded documents using advanced RAG pipeline
- **Semantic Search**: Intelligent retrieval of relevant document sections
- **Production Architecture**: Modular, scalable backend design

### Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **Database**: PostgreSQL with vector extensions
- **AI/ML**: OpenAI API, Sentence Transformers
- **Authentication**: JWT, bcrypt password hashing
- **Document Processing**: PyMuPDF for PDF text extraction

## Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database (or SQLite for development)
- OpenAI API key (for LLM functionality)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Swatijha-22/ai-business-assisstant.git
   cd ai-business-assisstant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL, OpenAI API key, etc.
   ```

5. **Run the application**
   ```bash
   python run_server.py
   ```

### API Documentation

Once running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Documentation

- **📚 [Development Journey](DEVELOPMENT_JOURNEY.md)**: Complete learning guide explaining every decision and implementation detail
- **🔧 [Technical Summary](TECHNICAL_SUMMARY.md)**: Professional technical overview of architecture and features  
- **📁 [Complete File Guide](Explain%20Files's%20Name-1.md)**: Detailed explanation of every file and folder in the project
- **📄 [Phase 3 Files Guide](Phase-3%20Files's%20names-%20explanation%20and%20logics.md)**: Comprehensive explanation of all Phase 3 additions and changes
- **📊 [Phase 3 Summary](PHASE_3_SUMMARY.md)**: Technical achievement summary for Phase 3
- **🔐 [Authentication Guide](AUTHENTICATION_GUIDE.md)**: Setup instructions for GitHub integration

## Development Phases

### ✅ Phase 1: Project Structure
- Clean, modular architecture
- FastAPI application setup
- Service layer abstraction

### 🔄 Phase 2: Authentication (In Progress)
- User registration and login
- JWT token management
- Database integration

### 📋 Phase 3: Document Processing
- PDF upload and validation
- Text extraction and chunking
- Embedding generation

### 🧠 Phase 4: RAG Pipeline
- Semantic search implementation
- LLM integration
- Answer generation

### 🧪 Phase 5: Testing & Polish
- Comprehensive test suite
- Error handling
- Production optimizations

## Architecture Overview

```
FastAPI Routes → Services → Database/AI
     ↓              ↓         ↓
   - Auth        - Document  - PostgreSQL
   - Documents   - Embedding - Vector Store  
   - Chat        - Retrieval - OpenAI API
                 - LLM
```

## Project Goals

This project demonstrates production-level skills in:
- **Backend Engineering**: FastAPI, REST APIs, database design
- **AI Engineering**: RAG pipelines, embeddings, LLM integration
- **Security**: Authentication, authorization, input validation
- **Architecture**: Modular design, service patterns, scalability

## Future Versions

- **Version 2**: Structured data analysis (CSV, Excel)
- **Version 3**: Automated reporting and workflows
- **Version 4**: Docker containerization and cloud deployment
- **Version 5**: Production dashboard and client features

## Contributing

This is a learning and portfolio project. See development phases above for current focus areas.

## License

[License details to be added]
