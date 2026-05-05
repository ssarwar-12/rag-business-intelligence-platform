# API

FastAPI backend for the Smart Enterprise RAG Knowledge Base.

## Phase 1 Scope

Implemented:

- FastAPI app setup.
- SQLAlchemy models for users, workspaces, documents, chunks, conversations, messages, and query logs.
- Alembic initial migration.
- Demo user creation.
- Health endpoint.
- Workspace create/list endpoints.
- Document upload/list metadata endpoints.

Not implemented yet:

- Document ingestion.
- Embeddings and vector search.
- RAG chat.
- Analytics endpoints.

## Local Commands

```bash
cd apps/api
python -m pip install -e ".[test]"
alembic upgrade head
uvicorn app.main:app --reload
pytest
```

Set configuration with `.env` or environment variables. Do not commit real `.env` files.
