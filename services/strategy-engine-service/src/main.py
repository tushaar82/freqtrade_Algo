"""
Strategy Engine Service
VELOX Trading Platform
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import FastAPI
from .config import settings
from .strategy_executor import StrategyExecutor

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="VELOX Strategy Engine Service",
    version="1.0.0",
    description="Trading strategy execution and signal generation"
)

# Global strategy executor
strategy_executor: StrategyExecutor = None


@app.on_event("startup")
async def startup_event():
    """Initialize strategy executor on startup"""
    global strategy_executor
    logger.info("Starting Strategy Engine Service...")
    strategy_executor = StrategyExecutor()
    
    # Start executor in background
    asyncio.create_task(strategy_executor.run())
    logger.info("Strategy Engine Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global strategy_executor
    logger.info("Shutting down Strategy Engine Service...")
    if strategy_executor:
        await strategy_executor.stop()
    logger.info("Strategy Engine Service stopped")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "strategy-engine",
        "active_strategies": len(strategy_executor.active_strategies) if strategy_executor else 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
