"""
Position Tracking Service
VELOX Trading Platform
"""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import FastAPI
from .config import settings
from .position_service import PositionService

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VELOX Position Tracking Service",
    version="1.0.0"
)

position_service: PositionService = None


@app.on_event("startup")
async def startup_event():
    global position_service
    logger.info("Starting Position Tracking Service...")
    position_service = PositionService()
    asyncio.create_task(position_service.run())
    logger.info("Position Tracking Service started")


@app.on_event("shutdown")
async def shutdown_event():
    global position_service
    if position_service:
        await position_service.stop()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "position-tracking"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
