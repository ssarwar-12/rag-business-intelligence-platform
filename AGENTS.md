# AGENTS.md

Guidance for future Codex tasks in this repository.

## Project

Smart Enterprise RAG Knowledge Base is a full-stack AI portfolio project. It should become a working SaaS-style app where users upload business documents, ingest them into a RAG pipeline, and chat with cited answers.

Primary stack:

- Frontend: Next.js, TypeScript, Tailwind CSS, Recharts.
- Backend: FastAPI, Python, Pydantic, SQLAlchemy, PostgreSQL, Alembic.
- AI/RAG: OpenAI API, vector store abstraction, local vector store by default, optional Pinecone.
- Infra: Docker, docker-compose, GitHub Actions.

## Current Expected Layout

```text
apps/
  api/
  web/
docs/
infra/
packages/
  shared/
README.md
AGENTS.md
.env.example
```

`packages/shared` is optional. Do not add shared packages unless they remove real duplication or support generated API types cleanly.

## Conventions

- Keep frontend and backend clearly separated.
- Prefer small modules with obvious names over broad utility files.
- Keep the MVP real: no fake responses, fake charts, or hardcoded analytics when API data exists.
- Use local vector search as the default development path.
- Keep Pinecone optional and configuration-driven.
- Use a demo user for initial auth. Do not spend major time on production auth until the core RAG workflow works.
- Store uploaded files locally in a configurable upload directory for the MVP.
- Use Alembic for database schema changes.
- Do not commit `.env` files or real secrets.
- Keep code readable for recruiters and future maintainers.

## Backend Conventions

Expected backend root: `apps/api`.

Suggested module boundaries:

- `app/api`: FastAPI routers and dependencies.
- `app/core`: settings, startup, demo-user bootstrap.
- `app/db`: SQLAlchemy session/base setup.
- `app/models`: SQLAlchemy models.
- `app/schemas`: Pydantic request/response schemas.
- `app/ingestion`: file loading, CSV summaries, chunking, ingestion orchestration.
- `app/rag`: prompting, retrieval, embeddings, chat orchestration.
- `app/vectorstores`: vector store interface and implementations.
- `tests`: backend tests.

Backend rules:

- Use SQLAlchemy 2.x style where practical.
- Use UUID identifiers.
- Store flexible metadata as PostgreSQL JSONB.
- Keep routes thin; put business logic in services or pipeline modules.
- Handle ingestion failures by setting document status to `failed` and saving `error_message`.
- Scope retrieval by `workspace_id`.
- Never hallucinate citations. Citation objects must map to stored chunks/documents.
- Make `RAG_TOP_K` configurable and default it to `5`.

## Frontend Conventions

Expected frontend root: `apps/web`.

Suggested module boundaries:

- `app`: Next.js app router pages.
- `components`: reusable UI components.
- `lib`: API client, formatting helpers, constants.
- `types`: TypeScript API/domain types.

Frontend rules:

- Use TypeScript.
- Use Tailwind CSS.
- Use Recharts for dashboard/admin charts.
- Use shadcn/ui only if it is already configured or cheap to add.
- Keep the visual style professional, quiet, and enterprise-oriented.
- Add loading and error states for API calls.
- Dashboards should use real backend data once endpoints exist.
- Avoid heavy frontend tests unless asked; at minimum keep `npm run build` passing.

## Documentation Conventions

Keep these docs current as implementation evolves:

- `README.md`: setup, features, architecture overview, env vars, known limitations.
- `docs/IMPLEMENTATION_PLAN.md`: phase plan and progress notes.
- `docs/ARCHITECTURE.md`: architecture and data flow.
- `docs/RAG_PIPELINE.md`: ingestion, chunking, embedding, retrieval, citation behavior.
- `docs/API_SPEC.md`: endpoint contracts and examples.

When changing API behavior, update `docs/API_SPEC.md`.

When changing ingestion or retrieval behavior, update `docs/RAG_PIPELINE.md`.

When changing major component boundaries, update `docs/ARCHITECTURE.md`.

## Commands

Commands are not finalized yet because the apps have not been scaffolded. Once created, prefer adding stable scripts and keeping this section updated.

Expected backend commands:

```bash
cd apps/api
pytest
alembic upgrade head
uvicorn app.main:app --reload
```

Expected frontend commands:

```bash
cd apps/web
npm install
npm run dev
npm run build
```

Expected infrastructure command:

```bash
docker compose -f infra/docker-compose.yml up --build
```

## Definition Of Done For Future Tasks

For implementation tasks, finish with:

- Files changed.
- Behavior implemented.
- Commands run.
- Test/build results.
- Known gaps or follow-up items.

A feature is not done if it only returns mocked data while the real backend path exists or is in scope for the task.

## Do-Not Rules

- Do not hardcode API keys.
- Do not commit `.env` files.
- Do not fake LLM responses.
- Do not fake charts with static data when real API data exists.
- Do not add unnecessary microservices.
- Do not overbuild authentication before core RAG works.
- Do not make the app dependent on paid-only services.
- Do not hide database changes outside Alembic migrations.
- Do not collapse unrelated backend behavior into one giant route file.
- Do not make broad refactors unrelated to the requested phase.
