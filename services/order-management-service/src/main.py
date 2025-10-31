"""
Order Management Service
VELOX Trading Platform
"""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import FastAPI
from .config import settings
from .order_service import OrderService

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VELOX Order Management Service",
    version="1.0.0",
    description="Order lifecycle management and execution"
)

order_service: OrderService = None


@app.on_event("startup")
async def startup_event():
    global order_service
    logger.info("Starting Order Management Service...")
    order_service = OrderService()
    asyncio.create_task(order_service.run())
    logger.info("Order Management Service started")


@app.on_event("shutdown")
async def shutdown_event():
    global order_service
    logger.info("Shutting down Order Management Service...")
    if order_service:
        await order_service.stop()
    logger.info("Order Management Service stopped")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "order-management",
        "pending_orders": len(order_service.pending_orders) if order_service else 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
