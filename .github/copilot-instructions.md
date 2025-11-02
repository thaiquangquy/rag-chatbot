# rag-chatbot Development Guidelines

**Last updated**: 2025-11-02

## Project Overview

RAG Chatbot is a retrieval-augmented generation chatbot for company wiki documentation using Google Docs as the source. The system includes document ingestion, vector search with FAISS, and LLM-powered answer synthesis with source attribution.

## Active Technologies

### Backend
- **Language**: Python 3.12
- **Framework**: FastAPI 0.115.0
- **Database**: PostgreSQL 15 (via SQLAlchemy 2.0.36)
- **Cache**: Redis 7
- **Vector Store**: FAISS (faiss-cpu 1.12.0)
- **LLM Provider**: OpenAI 1.14.3
- **Observability**: OpenTelemetry, Prometheus
- **Testing**: pytest 7.4.4 + testcontainers 3.7.1

### Frontend
- **Language**: TypeScript 5.3.3
- **Framework**: React 18.3.1
- **Build Tool**: Vite 5.1.0

### Infrastructure
- **Containerization**: Docker Compose
- **Database Migrations**: Alembic

## Project Structure

```
backend/
├── src/
│   ├── api/          # FastAPI routes and main app
│   ├── cli/          # CLI commands for ingestion
│   ├── config/       # Application settings
│   ├── integrations/ # External service clients (Google Docs)
│   ├── lib/          # Core utilities (chunking, embedding)
│   ├── middleware/   # Auth, audit logging
│   ├── models/       # ORM entities and Pydantic schemas
│   ├── observability/# OpenTelemetry setup
│   ├── providers/    # LLM provider abstractions
│   ├── services/     # Business logic (ingest, retrieval, answer)
│   ├── utils/        # Helper functions
│   └── vector/       # FAISS index wrapper
├── tests/
│   ├── unit/         # Unit tests
│   ├── contract/     # API contract tests
│   └── integration/  # Integration tests
├── alembic/          # Database migrations
├── requirements.txt  # Python dependencies
└── pyproject.toml    # Tool configurations (ruff, black, pytest)

frontend/
├── src/
│   ├── components/   # React components (ChatWindow, MessageList, etc.)
│   ├── pages/        # Page components
│   └── services/     # API client
├── package.json      # Node dependencies and scripts
└── tsconfig.json     # TypeScript configuration

specs/                # Feature specifications and planning
docker-compose.yml    # Local development services (Postgres, Redis)
```

## Development Commands

### Backend

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run tests (all)
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/contract/
pytest tests/integration/

# Lint code
ruff check .

# Format code
black .

# Start FastAPI development server (manual)
uvicorn src.api.main:app --reload

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint (currently not configured)
npm run lint
```

### Infrastructure

```bash
# Start local services (PostgreSQL, Redis)
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

## Code Style

### Python
- **Line length**: 100 characters (configured in pyproject.toml)
- **Formatter**: black
- **Linter**: ruff (enforces: E, F, I, UP)
- **Type hints**: Use Python type annotations throughout
- **Imports**: Organized by ruff (isort rules)

### TypeScript/React
- **Strict mode**: Enabled in tsconfig.json
- **Components**: Functional components with hooks
- **Formatting**: Follow standard TypeScript conventions

## Testing Guidelines

### Backend Testing Strategy
- **Unit tests** (`tests/unit/`): Test individual functions and classes
- **Contract tests** (`tests/contract/`): Validate API endpoint contracts (request/response shapes)
- **Integration tests** (`tests/integration/`): Test end-to-end flows with real dependencies

### Test Requirements
- Use `pytest` for all Python tests
- Use `testcontainers` for ephemeral PostgreSQL in integration tests
- Mock external services (OpenAI, Google Docs) in unit tests
- Test with real services where appropriate in integration tests

## Key Patterns and Conventions

### Backend
- **Settings**: Use `pydantic-settings` for configuration (see `src/config/settings.py`)
- **Database**: SQLAlchemy ORM for all database operations
- **Async**: Use `async/await` for I/O-bound operations
- **Error handling**: Structured error responses with appropriate HTTP status codes
- **Logging**: Structured JSON logging for observability
- **Authentication**: API key middleware for secure endpoints

### Frontend
- **State management**: React hooks (useState, useEffect)
- **API calls**: Centralized in `services/api.ts`
- **Component structure**: Keep components focused and reusable

## Development Workflow

1. **Before making changes**: Run existing tests to understand baseline
2. **Make minimal changes**: Focus on the specific requirement
3. **Test early and often**: Run relevant tests after each change
4. **Lint before committing**: Ensure code passes ruff and black checks
5. **Integration tests**: Validate end-to-end flows for feature changes

## Environment Setup

### Required Environment Variables
- Database connection (for PostgreSQL)
- Redis connection string
- OpenAI API key (or Ollama endpoint)
- Google Docs service account credentials
- See `.env.example` if available, or check `src/config/settings.py` for required settings

### Local Development
1. Start infrastructure: `docker-compose up -d`
2. Run migrations: `cd backend && alembic upgrade head`
3. Start backend: `cd backend && uvicorn src.api.main:app --reload`
4. Start frontend: `cd frontend && npm run dev`

## Recent Changes
- **001-rag-chatbot-wiki**: Initial RAG chatbot implementation with multi-document context ingestion, quick answer lookup, and source attribution

## Notes for AI Assistants

- The project uses separate backend and frontend directories
- Backend testing uses three layers: unit, contract, and integration
- Always run tests before and after making changes
- Use existing patterns for new features (see similar implementations)
- Keep test coverage comprehensive but focused
- Performance targets: <3s chat response (p95), <5min indexing for <1MB docs

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
