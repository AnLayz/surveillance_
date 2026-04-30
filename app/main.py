import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import alerts, detections, stats, stream, dashboard
from app.core.config import settings
from app.cv.pipeline import SurveillancePipeline
from app.database.base import Base
from app.database.session import engine
import app.models  # noqa: F401 — registers all ORM models with Base.metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Single shared pipeline instance — routes can reference it if needed
pipeline = SurveillancePipeline(
    camera_id=1,
    zone_file="zones/camera_1.json",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on first run (Alembic handles migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start CV pipeline in the background
    pipeline.start()

    yield  # application runs here

    # Graceful shutdown
    pipeline.stop()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="Smart Surveillance System with Computer Vision",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.include_router(detections.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(stream.router, prefix="/api/v1")
app.include_router(dashboard.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name}
