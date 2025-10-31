"""
Order Service - Order Lifecycle Management
VELOX Trading Platform
"""
import asyncio
import logging
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from .paper_trading import PaperTradingSimulator
from .kafka_consumer import SignalEventConsumer
from .kafka_producer import OrderEventProducer
from .models.order import Order, OrderSide, OrderType, OrderStatus

logger = logging.getLogger(__name__)


class OrderService:
    """Manage order lifecycle and execution"""
    
    def __init__(self):
        self.paper_trading = PaperTradingSimulator()
        self.order_producer = OrderEventProducer()
        self.signal_consumer = None
        self.pending_orders: dict[UUID, Order] = {}
        self.running = False
    
    async def run(self) -> None:
        self.running = True
        logger.info("Order service started")
        
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self._start_signal_consumer)
    
    def _start_signal_consumer(self) -> None:
        self.signal_consumer = SignalEventConsumer(self._on_signal_event)
        self.signal_consumer.start()
    
    def _on_signal_event(self, event: dict[str, Any]) -> None:
        """Process signal event and create order"""
        try:
            payload = event.get("payload", {})
            signal_type = payload["signal_type"]
            
            # Determine order side from signal type
            if "LONG" in signal_type:
                side = OrderSide.BUY if "ENTRY" in signal_type else OrderSide.SELL
            elif "SHORT" in signal_type:
                side = OrderSide.SELL if "ENTRY" in signal_type else OrderSide.BUY
            else:
                logger.warning(f"Unknown signal type: {signal_type}")
                return
            
            # Create order
            order = Order(
                id=uuid4(),
                strategy_id=UUID(payload["strategy_id"]),
                instrument_id=UUID(payload["instrument_id"]),
                side=side,
                order_type=OrderType.MARKET,
                quantity=payload["recommended_quantity"],
                mode="PAPER",  # Always paper for now
                status=OrderStatus.PENDING
            )
            
            self.pending_orders[order.id] = order
            
            # Execute in paper trading mode
            current_price = payload["recommended_price"]
            if self.paper_trading.execute_order(order, current_price):
                self._publish_order_event(order)
            
            # Remove from pending
            if order.id in self.pending_orders:
                del self.pending_orders[order.id]
        
        except Exception as e:
            logger.error(f"Error processing signal event: {e}", exc_info=True)
    
    def _publish_order_event(self, order: Order) -> None:
        """Publish order event to Kafka"""
        order_event = {
            "order_id": str(order.id),
            "strategy_id": str(order.strategy_id),
            "instrument_id": str(order.instrument_id),
            "symbol": "UNKNOWN",  # Would be fetched from database
            "side": order.side.value,
            "order_type": order.order_type.value,
            "quantity": order.quantity,
            "filled_quantity": order.filled_quantity,
            "average_fill_price": float(order.average_fill_price) if order.average_fill_price else None,
            "status": order.status.value,
            "mode": order.mode,
            "broker_order_id": order.broker_order_id,
            "fills": order.fills if isinstance(order.fills, list) else [],
            "timestamp": datetime.utcnow().isoformat()
        }
        self.order_producer.publish_order_event(order_event)
    
    async def stop(self) -> None:
        self.running = False
        logger.info("Stopping order service...")
        
        if self.signal_consumer:
            self.signal_consumer.stop()
        self.order_producer.close()
        
        logger.info("Order service stopped")
