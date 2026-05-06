# Smart Enterprise RAG Knowledge Base Architecture

## Overview

Smart Enterprise RAG Knowledge Base is a monorepo full-stack application with a Next.js frontend, FastAPI backend, PostgreSQL database, local file storage, and a pluggable vector store. The MVP supports a demo-user workflow where users create workspaces, upload enterprise documents, ingest files into searchable chunks, and ask questions that return grounded answers with citations.

## High-Level Components

```text
Next.js Web App
  |
  | HTTP/JSON
  v
FastAPI Backend
  |
  | SQLAlchemy
  v
PostgreSQL

FastAPI Backend
  |
  | local filesystem
  v
Upload Storage

FastAPI Backend
  |
  | embeddings / generation
  v
OpenAI API

FastAPI Backend
  |
  | vector upsert/query
  v
Vector Store
  |-- Local vector store for development
  |-- Pinecone implementation for hosted vector search
```

## Intended Repository Boundaries

```text
apps/api
```

FastAPI application, database models, Alembic migrations, ingestion pipeline, RAG services, vector store implementations, and backend tests.

```text
apps/web
```

Next.js application, dashboard pages, upload/chat/admin UI, API client, frontend types, and UI components.

```text
docs
```

Architecture, API specification, RAG pipeline details, and implementation plan.

```text
infra
```

Docker compose and local infrastructure support.

```text
packages/shared
```

Optional shared types or generated OpenAPI artifacts. This should remain absent or minimal unless it earns its keep.

## Backend Responsibilities

The FastAPI backend owns:

- Health check endpoint.
- Demo-user initialization.
- Workspace creation and listing.
- Upload validation and local file storage.
- Document metadata and ingestion status.
- File extraction for PDF, TXT, Markdown, and CSV.
- Chunking and approximate token counting.
- Embedding generation.
- Vector upsert and search.
- RAG prompt construction.
- OpenAI chat completion calls.
- Conversation and message persistence.
- Query logging.
- Analytics aggregation.

## Frontend Responsibilities

The Next.js frontend owns:

- Product landing page.
- Dashboard overview.
- Workspace navigation.
- Document upload and ingestion controls.
- Document status display.
- Chat interface.
- Citation presentation.
- Admin analytics visualizations using Recharts.
- Loading and error states.
- API client layer and TypeScript response types.

The frontend should call real backend APIs for dashboard and analytics data. Static placeholder charts should be avoided once the corresponding endpoint exists.

## Database Schema Summary

Expected PostgreSQL tables:

- `users`: demo user records.
- `workspaces`: workspace ownership and names.
- `documents`: uploaded file metadata, storage path, type, and ingestion status.
- `document_chunks`: chunk text, metadata, approximate token counts, and vector ids.
- `conversations`: chat conversation containers.
- `messages`: user and assistant messages.
- `query_logs`: query text, latency, retrieved chunk ids, and analytics source data.

Expected model fields:

```text
User
- id
- email
- created_at

Workspace
- id
- name
- owner_id
- created_at

Document
- id
- workspace_id
- filename
- file_type
- storage_path
- status
- error_message
- created_at
- updated_at

DocumentChunk
- id
- document_id
- workspace_id
- chunk_index
- text
- token_count
- metadata
- vector_id
- created_at

Conversation
- id
- workspace_id
- title
- created_at

Message
- id
- conversation_id
- role
- content
- metadata
- created_at

QueryLog
- id
- workspace_id
- conversation_id
- query
- latency_ms
- retrieved_chunk_ids
- created_at
```

## Ingestion Data Flow

```text
Upload file
  -> validate extension and content type
  -> save file to UPLOAD_DIR
  -> create Document row with status=uploaded
  -> ingest request
  -> set status=processing
  -> extract text or structured CSV content
  -> split into overlapping chunks
  -> generate embeddings
  -> insert DocumentChunk rows
  -> upsert vectors with workspace/document metadata
  -> set status=completed
```

If any ingestion stage fails, the backend should set `Document.status=failed` and persist a concise `error_message`.

## RAG Query Data Flow

```text
User asks a question
  -> create or reuse conversation
  -> save user message
  -> embed query
  -> vector search scoped by workspace_id
  -> fetch matching chunks from PostgreSQL
  -> build grounded prompt
  -> call OpenAI chat model
  -> build citations from retrieved chunks used
  -> save assistant message
  -> save query log
  -> return answer, citations, and conversation_id
```

The assistant should answer only from retrieved context. If retrieved context is insufficient, it should say the uploaded documents do not contain enough information.

## Vector Store Abstraction

The backend should expose a small interface:

```python
class VectorStore:
    def upsert(self, chunks: list[EmbeddedChunk]) -> None: ...
    def query(self, workspace_id: str, query_embedding: list[float], top_k: int) -> list[SearchResult]: ...
    def delete_document(self, document_id: str) -> None: ...
```

`VECTOR_STORE=local` should be the default for development. `VECTOR_STORE=pinecone` can be enabled when Pinecone configuration is present.

## API Surface

Minimum endpoints:

- `GET /health`
- `POST /workspaces`
- `GET /workspaces`
- `POST /workspaces/{workspace_id}/documents/upload`
- `GET /workspaces/{workspace_id}/documents`
- `POST /workspaces/{workspace_id}/documents/{document_id}/ingest`
- `POST /workspaces/{workspace_id}/chat`
- `GET /workspaces/{workspace_id}/conversations`
- `GET /workspaces/{workspace_id}/analytics`

The detailed request and response contracts should live in `docs/API_SPEC.md`.

## Environment Configuration

Backend:

- `DATABASE_URL`
- `OPENAI_API_KEY`
- `VECTOR_STORE`
- `PINECONE_API_KEY`
- `PINECONE_INDEX`
- `UPLOAD_DIR`
- `RAG_TOP_K`

Frontend:

- `NEXT_PUBLIC_API_URL`

Secrets must stay in untracked `.env` files. Example files should use placeholders only.

## Local Development Shape

Preferred local setup:

- PostgreSQL via Docker Compose.
- FastAPI backend run locally or through Docker.
- Next.js frontend run locally for fast iteration.
- Local vector store enabled by default.

Full Docker Compose can include backend and frontend once app entrypoints are stable.

## Phase 1 Backend Shape

The backend now exists under `apps/api` with:

- FastAPI application entrypoint in `app/main.py`.
- SQLAlchemy session setup in `app/db/session.py`.
- Declarative models in `app/models`.
- Pydantic schemas in `app/schemas`.
- Routers in `app/api/routes`.
- Alembic migration files in `alembic`.

At startup, the API can create tables automatically when `AUTO_CREATE_TABLES=true`, then ensures a demo user exists. Alembic remains the intended schema management path for PostgreSQL-backed development.

Implemented Phase 1 routes:

- `GET /health`
- `POST /workspaces`
- `GET /workspaces`
- `POST /workspaces/{workspace_id}/documents/upload`
- `GET /workspaces/{workspace_id}/documents`

## Phase 2 Ingestion Shape

The backend now includes ingestion modules under `app/ingestion`:

- `loaders.py`: PDF, TXT, Markdown, and CSV extraction.
- `csv_summary.py`: CSV column, row, numeric, and missing-value summaries.
- `chunking.py`: character-based chunking with overlap and source metadata.
- `pipeline.py`: document status transitions and chunk persistence.

The vector store abstraction now exists under `app/vectorstores`. Phase 2 defines the protocol and local JSON-backed vector store, but ingestion does not generate embeddings or upsert vectors yet.

Implemented Phase 2 route:

- `POST /workspaces/{workspace_id}/documents/{document_id}/ingest`

## Extension Points

Likely future improvements:

- Real authentication and workspace membership.
- Background ingestion jobs instead of synchronous ingestion.
- Streaming chat responses.
- Document deletion and vector cleanup.
- Rich PDF citation page previews.
- OpenAPI-generated frontend types.
- Hosted vector store deployment.
- Cloud object storage for uploads.
