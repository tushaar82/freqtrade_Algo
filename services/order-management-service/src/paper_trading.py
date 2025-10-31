"""
Paper Trading Simulator
VELOX Trading Platform
"""
import logging
import random
from datetime import datetime
from typing import Optional

from .models.order import Order, OrderType
from .order_state_machine import OrderStateMachine

logger = logging.getLogger(__name__)


class PaperTradingSimulator:
    """Simulate order execution for paper trading"""
    
    def __init__(self):
        self.slippage_percent = 0.05  # 0.05% slippage
        self.fill_probability = 0.95  # 95% fill rate
    
    def execute_order(self, order: Order, current_price: float) -> bool:
        """
        Simulate order execution
        
        Args:
            order: Order to execute
            current_price: Current market price
        
        Returns:
            True if order executed, False otherwise
        """
        # Simulate order submission
        if not OrderStateMachine.transition(order, OrderStatus.SUBMITTED):
            return False
        
        # Simulate broker acknowledgment
        OrderStateMachine.transition(order, OrderStatus.ACKNOWLEDGED)
        
        # Simulate fill probability (some orders may not fill)
        if random.random() > self.fill_probability:
            OrderStateMachine.transition(order, OrderStatus.REJECTED, "Simulated rejection - insufficient liquidity")
            return False
        
        # Calculate fill price with slippage
        fill_price = self._calculate_fill_price(order, current_price)
        
        # Simulate fill
        OrderStateMachine.add_fill(order, order.quantity, fill_price)
        
        logger.info(f"Paper trade executed: {order.side} {order.quantity} @ {fill_price}")
        return True
    
    def _calculate_fill_price(self, order: Order, current_price: float) -> float:
        """Calculate fill price with simulated slippage"""
        slippage = current_price * (self.slippage_percent / 100)
        
        if order.order_type == OrderType.MARKET:
            # Market orders: add slippage in unfavorable direction
            if order.side.value == "BUY":
                return current_price + slippage
            else:
                return current_price - slippage
        
        elif order.order_type == OrderType.LIMIT:
            # Limit orders: fill at limit price if market allows
            if order.price:
                if order.side.value == "BUY" and current_price <= float(order.price):
                    return float(order.price)
                elif order.side.value == "SELL" and current_price >= float(order.price):
                    return float(order.price)
            return current_price
        
        elif order.order_type in [OrderType.STOP_LOSS, OrderType.STOP_LOSS_MARKET]:
            # Stop orders: fill at market with slippage
            if order.side.value == "BUY":
                return current_price + slippage
            else:
                return current_price - slippage
        
        return current_price
