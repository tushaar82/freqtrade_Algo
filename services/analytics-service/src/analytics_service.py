"""Analytics Service Orchestration"""
import asyncio
import logging
from .pnl_calculator import PnLCalculator
from .metrics import MetricsCalculator
from .kafka_consumer import AnalyticsEventConsumer
from .pnl_publisher import PnLPublisher

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.pnl_calc = PnLCalculator()
        self.metrics_calc = MetricsCalculator()
        self.publisher = PnLPublisher()
        self.consumer = None
    
    async def run(self):
        logger.info("Analytics service started")
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self._start_consumer)
    
    def _start_consumer(self):
        self.consumer = AnalyticsEventConsumer(self._on_event)
        self.consumer.start()
    
    def _on_event(self, event: dict):
        try:
            payload = event.get("payload", {})
            event_type = event.get("event_type", "")
            
            if "position" in event_type.lower():
                self.pnl_calc.update_position_pnl(payload)
                pnl_data = self.pnl_calc.get_strategy_pnl(payload["strategy_id"])
                pnl_data["strategy_id"] = payload["strategy_id"]
                pnl_data["type"] = "PNL_UPDATE"
                self.publisher.publish_pnl_update(pnl_data)
            
            elif "trade" in event_type.lower():
                self.pnl_calc.update_trade_pnl(payload)
        
        except Exception as e:
            logger.error(f"Error processing analytics event: {e}", exc_info=True)
    
    async def stop(self):
        if self.consumer:
            self.consumer.stop()
