# AI Legacy Modernization Platform

An enterprise-oriented platform for analyzing legacy applications, assessing technical risk, and generating AI-driven modernization strategies with exportable executive reports.

Upload a legacy codebase as a ZIP archive, and the platform performs static code analysis, dependency intelligence, and a multi-agent LangGraph workflow powered by OpenAI. Results are persisted, visualized in a React dashboard, and exportable as PDF enterprise reports.

---

## Overview

Modernizing legacy systems is slow and knowledge-intensive. Teams must understand architecture, dependencies, business capabilities, and technical risk before planning a migration. This platform automates that discovery phase by combining deterministic static analysis with a sequential AI agent pipeline.

### End-to-end workflow

1. **Upload** — A legacy application ZIP is uploaded via the REST API or React UI.
2. **Ingestion** — Supported source files are extracted, stored, and analyzed during ingestion.
3. **Static analysis** — Classes, methods, and import dependencies are extracted (Java fully supported).
4. **AI pipeline** — A LangGraph workflow runs ten specialized agents to produce architecture insights, business capabilities, documentation, modernization plans, code recommendations, and a phased roadmap.
5. **Persistence** — Analysis results are cached as JSON snapshots in PostgreSQL.
6. **Visualization** — The React dashboard displays architecture, dependencies, risk, and modernization output.
7. **Reporting** — Enterprise PDF reports are generated on demand from persisted analysis snapshots.
8. **History** — Previously uploaded projects and report status are browsable from the history page.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Legacy application upload** | Secure ZIP ingestion with size limits, path validation, and supported file-type enforcement |
| **Static code analysis** | Extracts classes, methods, and dependencies from uploaded source files |
| **Dependency analysis** | Rule-based dependency intelligence with technology classification and risk levels |
| **Technical risk assessment** | Aggregates high-risk dependencies into an overall risk rating |
| **Architecture understanding** | LLM-driven grouping of classes into logical architecture components |
| **Business capability extraction** | Maps technical components to business capabilities |
| **RAG-powered modernization knowledge** | Retrieves relevant guidance from an embedded knowledge base using pgvector |
| **AI-generated architecture report** | Produces structured documentation of the legacy application |
| **Modernization planning** | Generates architecture assessment, risks, steps, and target architecture |
| **Code modernization recommendations** | Suggests concrete code-level modernization opportunities |
| **Multi-phase modernization roadmap** | Prioritized phased roadmap with business and technical context |
| **Enterprise PDF report generation** | Exports a formatted PDF suitable for stakeholder review |
| **Project history** | Lists uploaded projects with analysis and report status |

---

## System Architecture

The platform follows a layered architecture: a React frontend communicates with a FastAPI backend, which orchestrates static analyzers, a LangGraph agent pipeline, RAG retrieval, and PostgreSQL persistence.

```mermaid
flowchart TB
    subgraph Client
        UI[React Dashboard]
    end

    subgraph Backend["FastAPI Backend"]
        API[REST API Layer]
        ING[Ingestion Service]
        ANA[Static Analyzers]
        MOD[Modernization Service]
        RPT[Report Service]
        RAG[RAG / Vector Store]
    end

    subgraph AI["AI Pipeline (LangGraph)"]
        AG1[Deterministic Agents]
        AG2[LLM Agents]
        LLM[OpenAI gpt-4.1-mini]
    end

    subgraph Data
        PG[(PostgreSQL + pgvector)]
    end

    UI --> API
    API --> ING
    API --> MOD
    API --> RPT
    ING --> ANA
    ING --> PG
    ANA --> PG
    MOD --> AG1
    AG1 --> AG2
    AG2 --> LLM
    AG2 --> RAG
    RAG --> PG
    MOD --> PG
    RPT --> PG
```

### AI workflow sequence

The modernization pipeline runs synchronously on the first request to `/projects/{id}/modernization-plan`. Subsequent requests return the cached snapshot.

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Svc as Modernization Service
    participant Graph as LangGraph Pipeline
    participant DB as PostgreSQL
    participant LLM as OpenAI
    participant RAG as pgvector RAG

    Client->>API: GET /projects/{id}/modernization-plan
    API->>Svc: generate_modernization_plan()
    Svc->>DB: Check for cached snapshot

    alt Snapshot exists
        DB-->>Svc: Cached payload
        Svc-->>API: Return cached result
    else First run
        Svc->>DB: Load classes, methods, dependencies
        Svc->>Graph: invoke(state)
        Graph->>Graph: CodeAnalyzerAgent
        Graph->>Graph: DependencyAgent
        Graph->>Graph: RiskAgent
        Graph->>LLM: ArchitectureUnderstandingAgent
        Graph->>LLM: BusinessCapabilityAgent
        Graph->>RAG: KnowledgeAgent
        Graph->>LLM: DocumentationAgent
        Graph->>LLM: ModernizationAgent
        Graph->>LLM: CodeModernizationAgent
        Graph->>LLM: ModernizationRoadmapAgent
        Graph-->>Svc: Complete state
        Svc->>DB: Persist analysis snapshot
        Svc-->>API: Return result
    end

    API-->>Client: ModernizationPlanResponse
```

---

## Technology Stack

### Backend

| Technology | Purpose |
|------------|---------|
| Python 3.14+ | Application runtime |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| SQLAlchemy 2 | ORM and database access |
| Alembic | Schema migrations |
| Pydantic v2 | Request/response validation |
| fpdf2 | PDF report generation |

### Frontend

| Technology | Purpose |
|------------|---------|
| React 19 | UI framework |
| TypeScript | Type-safe frontend code |
| Vite 6 | Build tool and dev server |
| Material UI (MUI) 6 | Component library |
| React Flow (`@xyflow/react`) | Interactive architecture diagram |
| React Router 7 | Client-side routing |

### Database

| Technology | Purpose |
|------------|---------|
| PostgreSQL 16 | Primary relational database |
| pgvector | Vector similarity search for RAG |

### AI / LLM

| Technology | Purpose |
|------------|---------|
| LangGraph | Multi-agent workflow orchestration |
| LangChain / LangChain OpenAI | LLM integration |
| OpenAI `gpt-4.1-mini` | Architecture, documentation, and planning generation |
| OpenAI `text-embedding-3-small` | Knowledge base embeddings (1536 dimensions) |

### DevOps

| Technology | Purpose |
|------------|---------|
| Docker Compose | Local PostgreSQL + pgvector container |
| Alembic | Database migration management |
| `.env` configuration | Environment-based settings |

### Testing

| Technology | Purpose |
|------------|---------|
| pytest | Test runner and discovery |
| FastAPI TestClient | API integration tests |
| `unittest.mock` | Agent and service unit tests |

---

## Project Structure

```
ai-legacy-modernization-platform/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph agents and workflow graph
│   │   ├── analyzers/       # Static code analyzers (Java)
│   │   ├── api/             # FastAPI route handlers
│   │   ├── core/            # Config, logging, exceptions, health, upload validation
│   │   ├── database/        # SQLAlchemy engine and session management
│   │   ├── middleware/      # Request logging middleware
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── rag/             # Embeddings, vector store, document loader, retriever
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic (ingestion, analysis, reports, LLM)
│   │   └── main.py          # Application entry point
│   ├── alembic/             # Database migrations
│   ├── test_*.py            # Automated test suite
│   ├── conftest.py          # pytest fixtures and test environment defaults
│   ├── pytest.ini           # pytest configuration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   └── src/
│       ├── components/      # Reusable UI components (dashboard sections, layout)
│       ├── hooks/           # React hooks (project analysis data fetching)
│       ├── pages/           # Upload, Dashboard, and History pages
│       ├── services/        # API client and report service
│       └── types/           # TypeScript API type definitions
├── docs/
│   └── knowledge_base/      # Reference documents ingested into the RAG vector store
├── docker-compose.yml       # Local PostgreSQL + pgvector
└── test-legacy-app/         # Sample legacy Java application for testing
```

---

## AI Agent Pipeline

The LangGraph workflow executes ten agents in a fixed sequence. Deterministic agents process structured metadata; LLM agents call OpenAI via `LLMService`.

| Agent | Type | Responsibility |
|-------|------|----------------|
| **CodeAnalyzerAgent** | Deterministic | Summarizes detected classes and methods from static analysis results |
| **DependencyAgent** | Deterministic | Aggregates dependencies and identifies high-risk entries |
| **RiskAgent** | Deterministic | Computes an overall technical risk level from dependency analysis |
| **ArchitectureUnderstandingAgent** | LLM | Infers high-level architecture components by grouping related classes |
| **BusinessCapabilityAgent** | LLM | Maps architecture components to business capabilities |
| **KnowledgeAgent** | RAG | Retrieves relevant modernization guidance from the pgvector knowledge base |
| **DocumentationAgent** | LLM | Generates a structured architecture report for the legacy application |
| **ModernizationAgent** | LLM | Produces a modernization strategy with assessment, risks, and target architecture |
| **CodeModernizationAgent** | LLM | Recommends code-level modernization opportunities with implementation guidance |
| **ModernizationRoadmapAgent** | LLM | Builds a prioritized, multi-phase modernization roadmap |

Each LLM agent includes graceful fallback behavior — if generation fails, the pipeline continues with empty default structures rather than aborting the entire workflow.

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `projects` | Uploaded legacy application projects with name, status, and timestamps |
| `code_files` | Individual source files extracted from uploaded ZIP archives |
| `code_classes` | Classes detected during static analysis |
| `code_methods` | Methods detected during static analysis, linked to classes |
| `code_dependencies` | Import dependencies extracted from source files |
| `project_analysis_snapshots` | Persisted JSON payloads from the completed AI pipeline |
| `enterprise_reports` | Generated PDF reports linked to analysis snapshots |
| `knowledge_documents` | Embedded reference documents for RAG retrieval (pgvector) |

---

## API Overview

Interactive API documentation is available at `http://127.0.0.1:8000/docs` when the backend is running.

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Lightweight liveness check |
| `GET` | `/ready` | Readiness check (database + configuration) |
| `GET` | `/` | Legacy health endpoint (backward compatible) |

### Upload

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/projects/upload` | Upload a legacy application ZIP archive |

### Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects/{project_id}/analysis` | Static analysis results (classes, methods, dependencies) |

### Modernization

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects/{project_id}/modernization-plan` | Run or retrieve the AI modernization pipeline output |

### Reporting

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects/history` | List all projects with analysis and report status |
| `GET` | `/projects/{project_id}/analysis-result` | Retrieve persisted analysis snapshot |
| `GET` | `/projects/{project_id}/reports` | List generated reports for a project |
| `GET` | `/projects/{project_id}/reports/{report_id}` | Report metadata |
| `POST` | `/projects/{project_id}/reports/generate` | Generate and download a PDF report |
| `GET` | `/projects/{project_id}/reports/{report_id}/download` | Download a previously generated PDF |

### Knowledge Base

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/knowledge/ingest` | Ingest reference documents into the vector store |
| `GET` | `/knowledge/search?query=...` | Semantic search over the knowledge base |

---

## Local Development Setup

### Prerequisites

- Python 3.14+
- Node.js 18+ and npm
- Docker and Docker Compose
- An OpenAI API key

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-legacy-modernization-platform.git
cd ai-legacy-modernization-platform
```

### 2. Start the database

```bash
docker compose up -d
```

This starts PostgreSQL 16 with the pgvector extension on port `5432`.

### 3. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Edit with your OpenAI API key
alembic upgrade head
```

### 4. Run the backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Swagger UI: `http://127.0.0.1:8000/docs`.

### 5. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The UI will be available at `http://127.0.0.1:5173`.

### 6. Ingest the knowledge base (optional)

Before running modernization analysis, ingest reference documents for RAG retrieval:

```bash
curl -X POST http://127.0.0.1:8000/knowledge/ingest
```

Reference documents are located in `docs/knowledge_base/`.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `postgresql://admin:password@localhost:5432/modernizer_db` | PostgreSQL connection string |
| `OPENAI_API_KEY` | Yes | — | OpenAI API key for LLM and embedding calls |
| `APP_NAME` | No | `AI Legacy Modernization Platform` | Application display name |
| `APP_VERSION` | No | `1.0.0` | Application version string |
| `APP_ENV` | No | `development` | Environment label (`development`, `production`) |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `CORS_ORIGINS` | No | `http://127.0.0.1:5173,http://localhost:5173` | Comma-separated allowed CORS origins |
| `MAX_UPLOAD_SIZE_BYTES` | No | `52428800` (50 MB) | Maximum ZIP upload size |
| `MAX_ZIP_FILES` | No | `5000` | Maximum number of files inside a ZIP archive |
| `MAX_UNCOMPRESSED_SIZE_BYTES` | No | `524288000` (500 MB) | Maximum total uncompressed archive size |

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | Yes | `http://127.0.0.1:8000` | Backend API base URL |

> **Note:** Never commit real API keys or secrets. Use `.env` files locally and keep them out of version control.

---

## Testing

The backend includes an automated test suite covering static analysis, AI agents, report generation, and production-hardening features.

### Run the complete test suite

```bash
cd backend
source venv/bin/activate
python -m pytest
```

This runs 42 unit tests by default. Integration tests that require a live database are excluded automatically.

### Run integration tests

```bash
python -m pytest -m integration
```

### Run individual test files

```bash
python -m pytest test_java_analyzer.py
python -m pytest test_production_hardening.py
python -m pytest test_architecture_agent.py
```

### Run tests as standalone scripts

Tests can also be executed directly (legacy runner pattern):

```bash
python test_report_service.py
python test_dependency_intelligence.py
```

> **Tip:** Always use the virtual environment's Python (`./venv/bin/python -m pytest`) rather than a system-wide pytest installation to ensure project dependencies are available.

---

## Production Readiness

Milestone **12C-A** added enterprise-grade backend engineering without changing API contracts or agent business logic.

| Capability | Implementation |
|------------|----------------|
| **Structured logging** | Application-wide logging with timestamps, log levels, and contextual fields (project ID, duration, endpoint) |
| **Global exception handling** | Centralized handlers returning consistent JSON error responses with error codes, messages, timestamps, and request paths |
| **Health / readiness endpoints** | `/health` for liveness; `/ready` for database and configuration checks |
| **Configuration validation** | Fail-fast startup validation for required environment variables |
| **Upload validation** | Configurable size limits, ZIP bomb protection, safe-path checks, and supported file-type enforcement |
| **Improved Swagger documentation** | Endpoint summaries, descriptions, and response documentation |
| **Automated testing** | pytest suite with API, agent, analyzer, and hardening test coverage |

---

## Future Enhancements

- Authentication and user management
- Multi-language static analyzers (Python, COBOL, etc.)
- Additional LLM provider support (Azure OpenAI, Anthropic, local models)
- Cloud deployment (AWS, Azure, GCP)
- CI/CD pipeline with automated testing and deployment
- Kubernetes deployment with horizontal scaling
- Real-time progress updates during long-running AI pipeline execution
- Dashboard sections for code modernization and roadmap visualization

---

## Screenshots

> Screenshots can be added here for portfolio presentation.

| Page | Placeholder |
|------|-------------|
| Upload page | `![Upload Page](docs/screenshots/upload-page.png)` |
| Analysis dashboard | `![Dashboard](docs/screenshots/dashboard.png)` |
| Architecture diagram | `![Architecture Diagram](docs/screenshots/architecture-diagram.png)` |
| PDF report export | `![PDF Export](docs/screenshots/pdf-export.png)` |
| Project history | `![History Page](docs/screenshots/history-page.png)` |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance Python API framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) for multi-agent workflow orchestration
- [LangChain](https://www.langchain.com/) and [OpenAI](https://openai.com/) for LLM and embedding integration
- [pgvector](https://github.com/pgvector/pgvector) for vector similarity search in PostgreSQL
- [Material UI](https://mui.com/) and [React Flow](https://reactflow.dev/) for the dashboard UI
- [fpdf2](https://py-pdf.github.io/fpdf2/) for PDF report generation
