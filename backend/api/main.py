"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.middleware import apply_middleware
from backend.api.routes import events, hotels, reports, excel, run
from backend.api.routes.local_agent_routes import router as local_agent_router
from backend.api.routes.voice_routes import router as voice_router
from backend.core.scheduler import start_scheduler, stop_scheduler, schedule_pipeline_run
from backend.db.database import create_tables
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("3atef API starting up...")
    create_tables()
    schedule_pipeline_run()
    start_scheduler()
    yield
    stop_scheduler()
    logger.info("3atef API shut down")


app = FastAPI(
    title="3atef — Event & Hotel Intelligence API",
    version="1.0.0",
    description="AI-powered event profitability and hotel price comparison agent",
    lifespan=lifespan,
)

apply_middleware(app)

app.include_router(run.router)
app.include_router(events.router)
app.include_router(hotels.router)
app.include_router(reports.router)
app.include_router(excel.router)
app.include_router(local_agent_router)
app.include_router(voice_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "3atef"}


if __name__ == "__main__":
    import uvicorn
    from backend.config import settings

    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=settings.API_PORT, reload=True)
