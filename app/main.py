from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.core.load_shed import LoadShedMiddleware, conversation_classifier
from app.api.v1.router import router as api_v1_router
from app.db.connection import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

if settings.LOAD_SHED_ENABLED:
    app.add_middleware(
        LoadShedMiddleware,
        classify=conversation_classifier(settings.API_PREFIX),
        limits=lambda: {"default": settings.LOAD_SHED_MAX_INFLIGHT},
        retry_after=lambda: settings.LOAD_SHED_RETRY_AFTER_SECONDS,
    )

app.include_router(api_v1_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME}"}
