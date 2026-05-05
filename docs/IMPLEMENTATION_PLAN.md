# Smart Enterprise RAG Knowledge Base Implementation Plan

## Project Goal

Build a production-quality full-stack portfolio project where users can upload PDFs, TXT/Markdown files, and CSVs into a workspace, ingest them through a Retrieval-Augmented Generation pipeline, and chat with the uploaded data using cited LLM answers.

The project should feel like a small internal SaaS product: clean dashboard, real ingestion, real vector retrieval, PostgreSQL-backed metadata, clear setup, and a readable architecture.

## Current Repository State

The repository currently contains only:

- `README.md`
- `.gitignore`

No application code, package manifests, backend files, frontend files, infrastructure files, or documentation beyond the README title exist yet.

## Target Repository Layout

```text
/
  apps/
    api/
      alembic/
      app/
        api/
        core/
        db/
        ingestion/
        models/
        rag/
        schemas/
        services/
        vectorstores/
      tests/
      pyproject.toml
      .env.example
      Dockerfile
    web/
      app/
      components/
      lib/
      types/
      package.json
      .env.example
      Dockerfile
  docs/
    API_SPEC.md
    ARCHITECTURE.md
    IMPLEMENTATION_PLAN.md
    RAG_PIPELINE.md
  infra/
    docker-compose.yml
  .github/
    workflows/
      ci.yml
  packages/
    shared/
  AGENTS.md
  README.md
  .env.example
```

`packages/shared` is optional and should only be kept if it meaningfully helps share generated API types, OpenAPI artifacts, or documentation between apps.

## Guiding Decisions

- Use a monorepo with clearly separated `apps/api` and `apps/web`.
- Keep authentication simple: create or seed a demo user and let the frontend operate through that demo context.
- Use PostgreSQL as the system of record for users, workspaces, documents, chunks, conversations, messages, and query logs.
- Store uploaded files locally in a configurable upload directory for the MVP.
- Define a `VectorStore` interface early so local vector search and Pinecone support can evolve independently.
- Prioritize local development reliability: `VECTOR_STORE=local` must work without paid external services.
- Avoid fake data paths. Dashboards should call real API endpoints, even if the dataset is small.
- Keep LangChain/LlamaIndex optional. Use direct OpenAI SDK calls unless a framework clearly reduces code and complexity.

## Phase 0: Repo Foundation And Documentation Skeleton

Goal: establish the monorepo shape, environment examples, and docs scaffolding without implementing business logic.

Create:

- `apps/api/.env.example`
- `apps/api/README.md`
- `apps/web/.env.example`
- `apps/web/README.md`
- `docs/API_SPEC.md`
- `docs/RAG_PIPELINE.md`
- `infra/docker-compose.yml` placeholder or initial service outline
- `.env.example`

Modify:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `AGENTS.md`

Expected contents:

- README skeleton with product overview, stack, setup placeholders, architecture overview, screenshots placeholder, limitations, and future improvements.
- Env examples with no real secrets.
- Docker compose outline for PostgreSQL first; backend/frontend services may be added once app entrypoints exist.

Validation:

- Confirm file layout with `rg --files`.
- Confirm no secrets or `.env` files are added.

Stop point:

- Summarize created structure and next phase.

## Phase 1: Backend Foundation

Goal: create a working FastAPI backend with database models, Alembic, demo-user seeding, and core workspace/document metadata endpoints.

Create:

- `apps/api/pyproject.toml`
- `apps/api/app/main.py`
- `apps/api/app/core/config.py`
- `apps/api/app/core/demo_user.py`
- `apps/api/app/db/session.py`
- `apps/api/app/db/base.py`
- `apps/api/app/models/user.py`
- `apps/api/app/models/workspace.py`
- `apps/api/app/models/document.py`
- `apps/api/app/models/document_chunk.py`
- `apps/api/app/models/conversation.py`
- `apps/api/app/models/message.py`
- `apps/api/app/models/query_log.py`
- `apps/api/app/schemas/workspace.py`
- `apps/api/app/schemas/document.py`
- `apps/api/app/api/deps.py`
- `apps/api/app/api/routes/health.py`
- `apps/api/app/api/routes/workspaces.py`
- `apps/api/app/api/routes/documents.py`
- `apps/api/alembic.ini`
- `apps/api/alembic/env.py`
- `apps/api/alembic/versions/<initial_revision>.py`
- `apps/api/tests/test_health.py`

Modify:

- `apps/api/README.md`
- `docs/API_SPEC.md`
- `docs/ARCHITECTURE.md`
- `AGENTS.md` if commands are finalized

Endpoints implemented:

- `GET /health`
- `POST /workspaces`
- `GET /workspaces`
- `POST /workspaces/{workspace_id}/documents/upload`
- `GET /workspaces/{workspace_id}/documents`

Implementation notes:

- Use SQLAlchemy 2.x style models.
- Use UUID primary keys.
- Use PostgreSQL JSONB for metadata fields.
- Validate upload file extensions and MIME types conservatively.
- Store files under `UPLOAD_DIR/<workspace_id>/<document_id>/<filename>`.
- Document status starts as `uploaded`.

Validation:

- `pytest`
- backend import check
- Alembic migration generation or migration application against local PostgreSQL when available

Stop point:

- Summarize endpoints, models, migration status, and commands.

## Phase 2: Ingestion Pipeline And Local Vector Store

Goal: parse uploaded files, chunk extracted content, create embeddings, store chunks, and index vectors with reliable status transitions.

Create:

- `apps/api/app/ingestion/loaders.py`
- `apps/api/app/ingestion/csv_summary.py`
- `apps/api/app/ingestion/chunking.py`
- `apps/api/app/ingestion/pipeline.py`
- `apps/api/app/rag/embeddings.py`
- `apps/api/app/vectorstores/base.py`
- `apps/api/app/vectorstores/local.py`
- `apps/api/app/vectorstores/pinecone.py`
- `apps/api/app/vectorstores/factory.py`
- `apps/api/app/schemas/ingestion.py`
- `apps/api/tests/test_chunking.py`
- `apps/api/tests/test_csv_summary.py`

Modify:

- `apps/api/app/api/routes/documents.py`
- `apps/api/app/models/document.py`
- `apps/api/app/models/document_chunk.py`
- `docs/RAG_PIPELINE.md`
- `docs/API_SPEC.md`
- `docs/ARCHITECTURE.md`

Endpoints implemented:

- `POST /workspaces/{workspace_id}/documents/{document_id}/ingest`

Pipeline stages:

1. Load uploaded file.
2. Extract text or structured content.
3. Chunk text with overlap.
4. Generate embeddings.
5. Store chunks in PostgreSQL.
6. Upsert vectors.
7. Mark document `completed` or `failed`.

File support:

- PDF: extract page-by-page text and preserve page metadata.
- TXT/MD: read raw text.
- CSV: parse with pandas, convert rows to chunkable text, and store dataset summary metadata.

Implementation notes:

- Default chunk size: 3000-4000 characters.
- Default overlap: 10-15%.
- Approximate token count with a simple heuristic unless a tokenizer is already added.
- Local vector store should be easiest for development. Prefer Chroma or FAISS if straightforward; otherwise use a clear local persistent implementation with normalized vector similarity and documented limitations.
- Pinecone implementation can be present but should fail clearly if required env vars are missing.
- On failure, save `Document.error_message` and set status to `failed`.

Validation:

- `pytest apps/api/tests/test_chunking.py apps/api/tests/test_csv_summary.py`
- Manual upload and ingest with TXT and CSV once backend can run

Stop point:

- Summarize supported file types, vector store behavior, and test results.

## Phase 3: RAG Chat, Citations, Conversations, And Analytics API

Goal: add end-to-end question answering over ingested chunks, save conversation history, log queries, and expose analytics.

Create:

- `apps/api/app/rag/prompting.py`
- `apps/api/app/rag/retrieval.py`
- `apps/api/app/rag/chat.py`
- `apps/api/app/schemas/chat.py`
- `apps/api/app/schemas/conversation.py`
- `apps/api/app/schemas/analytics.py`
- `apps/api/app/api/routes/chat.py`
- `apps/api/app/api/routes/conversations.py`
- `apps/api/app/api/routes/analytics.py`
- `apps/api/tests/test_prompting.py`

Modify:

- `apps/api/app/main.py`
- `apps/api/app/models/conversation.py`
- `apps/api/app/models/message.py`
- `apps/api/app/models/query_log.py`
- `docs/API_SPEC.md`
- `docs/RAG_PIPELINE.md`
- `docs/ARCHITECTURE.md`

Endpoints implemented:

- `POST /workspaces/{workspace_id}/chat`
- `GET /workspaces/{workspace_id}/conversations`
- `GET /workspaces/{workspace_id}/analytics`

RAG flow:

1. Embed user query.
2. Query vector store by `workspace_id`.
3. Load matching chunks from PostgreSQL.
4. Build a grounded prompt with citation rules.
5. Call OpenAI chat model.
6. Return answer and citation objects.
7. Save user and assistant messages.
8. Save query log with latency and retrieved chunk ids.

Implementation notes:

- `RAG_TOP_K` defaults to `5`.
- Assistant must answer only from context.
- If context is insufficient, answer that uploaded documents do not contain enough information.
- Citations should include `document_id`, `document_name`, `chunk_id`, optional `page`, and `preview`.
- Do not fabricate filenames, numbers, or claims.

Analytics fields:

- uploaded document count
- chunk count
- questions asked
- common query terms
- document type breakdown
- ingestion status counts
- CSV numeric summaries when available

Validation:

- `pytest`
- Manual end-to-end TXT ingestion and chat when OpenAI key is available
- Prompt test verifies insufficient-context instruction is present

Stop point:

- Summarize RAG behavior, citations, analytics fields, and any dependency on OpenAI credentials.

## Phase 4: Frontend Foundation And Product UI

Goal: build a polished Next.js dashboard that consumes real backend APIs.

Create:

- `apps/web/package.json`
- `apps/web/next.config.ts`
- `apps/web/tsconfig.json`
- `apps/web/tailwind.config.ts`
- `apps/web/postcss.config.mjs`
- `apps/web/app/layout.tsx`
- `apps/web/app/page.tsx`
- `apps/web/app/dashboard/page.tsx`
- `apps/web/app/workspaces/[id]/documents/page.tsx`
- `apps/web/app/workspaces/[id]/chat/page.tsx`
- `apps/web/app/workspaces/[id]/admin/page.tsx`
- `apps/web/components/app-shell.tsx`
- `apps/web/components/status-badge.tsx`
- `apps/web/components/upload-dropzone.tsx`
- `apps/web/components/citation-list.tsx`
- `apps/web/components/analytics-charts.tsx`
- `apps/web/lib/api-client.ts`
- `apps/web/lib/formatters.ts`
- `apps/web/types/api.ts`

Modify:

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/API_SPEC.md`
- `AGENTS.md`

Pages:

- `/`: product landing page with concise explanation and clear navigation into dashboard.
- `/dashboard`: workspace overview and key metrics.
- `/workspaces/[id]/documents`: upload, list documents, trigger ingestion, view errors.
- `/workspaces/[id]/chat`: conversation sidebar, chat messages, citations.
- `/workspaces/[id]/admin`: Recharts analytics dashboard.

Implementation notes:

- Use TypeScript types throughout.
- Use a small API client layer.
- Use real loading and error states.
- Use Tailwind CSS.
- Use Recharts for analytics.
- Use shadcn/ui only if setup cost is reasonable and does not distract from MVP delivery.
- Keep visual design quiet, dense, and professional like an internal enterprise tool.

Validation:

- `npm run lint` if configured
- `npm run build`
- Manual browser smoke test

Stop point:

- Summarize frontend routes, API integration, and build status.

## Phase 5: Docker, CI, Final Docs, And Polish

Goal: make the project reproducible and resume-ready.

Create:

- `apps/api/Dockerfile`
- `apps/web/Dockerfile`
- `infra/docker-compose.yml`
- `.github/workflows/ci.yml`

Modify:

- `README.md`
- `docs/API_SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/RAG_PIPELINE.md`
- `AGENTS.md`
- root `.env.example`

Docker compose services:

- `postgres`
- `api`
- `web` if stable and not too slow for local iteration

CI checks:

- Backend install
- Backend tests
- Frontend install
- Frontend build
- Basic formatting or lint checks if configured

Documentation finalization:

- Setup instructions
- Environment variable reference
- Ingestion walkthrough
- Chat walkthrough
- Screenshots placeholder section
- Known limitations
- Future improvements
- Resume bullet suggestions

Validation:

- `docker compose -f infra/docker-compose.yml up --build`
- backend tests
- frontend build
- CI config sanity check

Stop point:

- Summarize all completed functionality, known limitations, and final commands.

## Definition Of Done

The project is done when:

- Backend runs locally.
- Frontend runs locally.
- User can upload at least one PDF or TXT file.
- User can ingest the file.
- User can ask a question about the file.
- Answer includes citations.
- User can upload a CSV and see basic analytics.
- Admin dashboard displays useful charts from real API data.
- README explains setup clearly.
- Code is organized into clear modules.
- Basic tests and frontend build pass.

## Constraints And Do-Not Rules

- Do not hardcode API keys.
- Do not commit `.env` files.
- Do not fake LLM responses.
- Do not fake charts with static data when real API data exists.
- Do not add unnecessary microservices.
- Do not spend major time on production authentication before core RAG works.
- Do not require paid-only services for local development.
- Do not collapse the backend into one giant file.
- Do not build complex abstractions before the simple path works.
- Do not make hidden schema changes without Alembic migrations.

## Phase Handoff Template

After each phase, report:

- What was implemented.
- Files created or modified.
- Commands run.
- Test/build results.
- Incomplete items or risks.
- Recommended next step.
