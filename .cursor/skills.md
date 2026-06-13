# AI Legacy Modernization Platform - Cursor Engineering Rules

## Your Role

Act as a senior backend + AI platform engineer.

You are helping build an enterprise-grade AI Legacy Modernization Platform.

The goal of this system is:
- analyze legacy applications
- understand code structure
- identify dependencies
- recommend modernization strategies
- generate migration plans using AI agents


## Technology Stack

Backend:
- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- Redis
- Docker

AI:
- LangGraph
- LangChain
- OpenAI APIs
- RAG architecture
- Agent orchestration

Frontend:
- React
- TypeScript


## Architecture Rules

Follow clean architecture principles.

Use this separation:

api/
- Contains FastAPI routes only
- Handles HTTP request/response
- No business logic here


services/
- Contains business logic
- Coordinates workflows
- Calls database layer


models/
- SQLAlchemy database models only


schemas/
- Pydantic request/response schemas


database/
- Database engine
- sessions
- connection management


agents/
- LangGraph AI agents


core/
- configuration
- logging
- shared utilities


## Coding Standards

Always:
- write production-quality code
- use type hints
- use dependency injection where appropriate
- keep functions small
- add meaningful error handling
- avoid duplicate code
- follow Python best practices


## FastAPI Guidelines

Routes should be thin.

Example:

API layer:
receive request

↓

Service layer:
perform logic

↓

Database layer:
persist data


Do not put:
- file parsing
- AI logic
- database operations

directly inside routes.


## Database Guidelines

Use:
- SQLAlchemy ORM
- explicit models
- relationships
- migrations-ready design

Design as if supporting thousands of uploaded applications.


## AI Agent Guidelines

Agents should have a single responsibility.

Examples:

CodeAnalyzerAgent:
understands source code


DependencyAgent:
extracts relationships


ModernizationAgent:
creates migration recommendations


RiskAgent:
detects migration risks


Use:
- structured outputs
- Pydantic validation
- traceable workflows


## Development Workflow

Implement incrementally.

Do not generate large amounts of unrelated code.

For every change:
1. Explain what files changed
2. Explain why
3. Explain how it fits the architecture


## Current Project Phase

Phase 1:
Backend foundation + legacy upload pipeline

Build:
- FastAPI APIs
- PostgreSQL storage
- file ingestion
- ZIP extraction

Do NOT implement AI agents until ingestion is complete.