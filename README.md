# Smart Enterprise RAG Knowledge Base

A full-stack AI portfolio project for uploading enterprise files, ingesting them into a retrieval pipeline, and chatting with the uploaded data using cited LLM answers.

## Tech Stack

- Frontend: Next.js, TypeScript, Tailwind CSS, Recharts
- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic
- Data: PostgreSQL-ready models with local SQLite fallback for quick development
- AI: OpenAI embeddings and chat completions
- Retrieval: local JSON-backed vector store behind a `VectorStore` abstraction

## Features

- Demo-user workspace flow
- Upload PDF, TXT, Markdown, and CSV files
- Persist uploaded files locally
- Extract, chunk, embed, and index documents
- Generate CSV summaries during ingestion
- Chat over workspace documents with citations
- Persist conversations, messages, and query logs
- Analytics endpoint and Recharts admin dashboard
- Clean frontend pages for dashboard, documents, chat, and analytics

## Local Setup

Backend:

```bash
cd apps/api
python -m pip install -e ".[test]"
copy .env.example .env
uvicorn app.main:app --reload
```

Set `OPENAI_API_KEY` in `apps/api/.env` before running ingestion or chat. Without it, ingestion and chat fail gracefully with clear configuration errors.

Frontend:

```bash
cd apps/web
npm install
copy .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Demo Workflow

1. Open `/dashboard` and create a workspace.
2. Open the workspace Documents page.
3. Upload a PDF, TXT, Markdown, or CSV file.
4. Click `Ingest` to extract, chunk, embed, and index the file.
5. Open Chat and ask a question about the uploaded document.
6. Review cited document snippets below the assistant answer.
7. Open Admin Analytics to review document, ingestion, question, and CSV summary metrics.

## Environment Variables

Backend examples live in `apps/api/.env.example`.

Important backend variables:

- `DATABASE_URL`
- `OPENAI_API_KEY`
- `UPLOAD_DIR`
- `VECTOR_STORE=local`
- `RAG_TOP_K=5`
- `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`
- `OPENAI_CHAT_MODEL=gpt-4o-mini`
- `BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`

Frontend examples live in `apps/web/.env.example`.

- `NEXT_PUBLIC_API_URL=http://localhost:8000`

## Validation

Backend:

```bash
cd apps/api
pytest
python -m compileall app alembic
```

Frontend:

```bash
cd apps/web
npm run build
```

## Known Limitations

- Authentication is intentionally simplified to a demo user.
- Chat responses are non-streaming.
- Pinecone is not implemented yet.
- Local vector storage is JSON-backed and meant for development/demo use.
- Docker Compose and GitHub Actions are planned polish items.
