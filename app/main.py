# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import chat, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="LLM Middleware", lifespan=lifespan)
app.include_router(chat.router,      prefix="/v1")
app.include_router(analytics.router, prefix="/v1")