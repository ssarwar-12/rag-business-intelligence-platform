# API

FastAPI backend for the Smart Enterprise RAG Knowledge Base.

## Current Scope

Implemented:

- FastAPI app setup.
- SQLAlchemy models for users, workspaces, documents, chunks, conversations, messages, and query logs.
- Alembic initial migration.
- Demo user creation.
- Health endpoint.
- Workspace create/list endpoints.
- Document upload/list metadata endpoints.
- Document ingestion endpoint.
- PDF, TXT, Markdown, and CSV extraction.
- CSV summary generation.
- Chunk storage in PostgreSQL.
- Local vector store abstraction.
- OpenAI embedding integration.
- Vector upsert during ingestion.
- RAG chat endpoint.
- Conversation and message persistence.
- Query logging.
- Conversation listing/detail endpoints.
- Workspace analytics endpoint.

Not implemented yet:

- Pinecone vector store implementation.
- Streaming chat.
- Production authentication.

## Local Commands

```bash
cd apps/api
python -m pip install -e ".[test]"
alembic upgrade head
uvicorn app.main:app --reload
pytest
```

Set configuration with `.env` or environment variables. Do not commit real `.env` files.

For ingestion and chat, set `OPENAI_API_KEY`. If the key is missing, ingestion marks documents failed with a clear error and chat returns `503 Service Unavailable`.
