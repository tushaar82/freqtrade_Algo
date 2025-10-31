"""
Analytics Service
VELOX Trading Platform
"""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import FastAPI
from .config import settings
from .analytics_service import AnalyticsService

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="VELOX Analytics Service", version="1.0.0")

analytics_service: AnalyticsService = None


@app.on_event("startup")
async def startup_event():
    global analytics_service
    logger.info("Starting Analytics Service...")
    analytics_service = AnalyticsService()
    asyncio.create_task(analytics_service.run())
    logger.info("Analytics Service started")


@app.on_event("shutdown")
async def shutdown_event():
    global analytics_service
    if analytics_service:
        await analytics_service.stop()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analytics"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
