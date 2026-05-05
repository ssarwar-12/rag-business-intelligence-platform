from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import documents, health, workspaces
from app.core.config import settings
from app.core.demo_user import ensure_demo_user
from app.db.base import Base
from app.db.session import SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_demo_user(db)
    yield


app = FastAPI(
    title="Smart Enterprise RAG Knowledge Base API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(workspaces.router)
app.include_router(documents.router)
