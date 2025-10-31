"""Position Service"""
import asyncio
import logging
from datetime import datetime
from uuid import UUID, uuid4

from .position_calculator import PositionCalculator
from .stop_loss_manager import StopLossManager
from .kafka_consumer import OrderEventConsumer
from .kafka_producer import PositionEventProducer
from .redis_cache import PositionCache

logger = logging.getLogger(__name__)

class PositionService:
    def __init__(self):
        self.calculator = PositionCalculator()
        self.stop_loss_mgr = StopLossManager()
        self.producer = PositionEventProducer()
        self.cache = PositionCache()
        self.consumer = None
        self.positions = {}
    
    async def run(self):
        logger.info("Position service started")
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self._start_consumer)
    
    def _start_consumer(self):
        self.consumer = OrderEventConsumer(self._on_event)
        self.consumer.start()
    
    def _on_event(self, event: dict):
        try:
            payload = event.get("payload", {})
            event_type = event.get("event_type", "")
            
            if "order" in event_type.lower():
                self._handle_order_event(payload)
            elif "market" in event_type.lower():
                self._handle_market_tick(payload)
        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)
    
    def _handle_order_event(self, order: dict):
        if order["status"] == "FILLED":
            position_id = str(uuid4())
            position = {
                "position_id": position_id,
                "strategy_id": order["strategy_id"],
                "instrument_id": order["instrument_id"],
                "side": "LONG" if order["side"] == "BUY" else "SHORT",
                "quantity": order["filled_quantity"],
                "entry_price": order["average_fill_price"],
                "current_price": order["average_fill_price"],
                "unrealized_pnl": 0,
                "status": "OPEN",
                "mode": order["mode"]
            }
            self.positions[position_id] = position
            self.cache.cache_position(position_id, position)
            self.producer.publish_position_event(position)
    
    def _handle_market_tick(self, tick: dict):
        instrument_id = tick["instrument_id"]
        current_price = float(tick["price"])
        
        for pos_id, pos in list(self.positions.items()):
            if pos["instrument_id"] == instrument_id and pos["status"] == "OPEN":
                pos["current_price"] = current_price
                pos["unrealized_pnl"] = self.calculator.calculate_unrealized_pnl(
                    pos["side"], pos["quantity"], pos["entry_price"], current_price
                )
                self.cache.cache_position(pos_id, pos)
                self.cache.publish_update(pos)
    
    async def stop(self):
        if self.consumer:
            self.consumer.stop()
        self.producer.close()
