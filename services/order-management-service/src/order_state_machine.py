"""
Order State Machine
VELOX Trading Platform
"""
import logging
from datetime import datetime
from typing import Optional

from .models.order import Order, OrderStatus

logger = logging.getLogger(__name__)


class OrderStateMachine:
    """Manage order state transitions"""
    
    # Valid state transitions
    TRANSITIONS = {
        OrderStatus.PENDING: [OrderStatus.SUBMITTED, OrderStatus.REJECTED, OrderStatus.CANCELLED],
        OrderStatus.SUBMITTED: [OrderStatus.ACKNOWLEDGED, OrderStatus.REJECTED, OrderStatus.CANCELLED],
        OrderStatus.ACKNOWLEDGED: [OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED, OrderStatus.REJECTED, OrderStatus.CANCELLED],
        OrderStatus.PARTIALLY_FILLED: [OrderStatus.FILLED, OrderStatus.CANCELLED],
        OrderStatus.FILLED: [],
        OrderStatus.REJECTED: [],
        OrderStatus.CANCELLED: []
    }
    
    @classmethod
    def can_transition(cls, current_status: OrderStatus, new_status: OrderStatus) -> bool:
        """Check if transition is valid"""
        return new_status in cls.TRANSITIONS.get(current_status, [])
    
    @classmethod
    def transition(cls, order: Order, new_status: OrderStatus, reason: Optional[str] = None) -> bool:
        """
        Transition order to new status
        
        Args:
            order: Order instance
            new_status: Target status
            reason: Optional reason for transition
        
        Returns:
            True if transition successful, False otherwise
        """
        if not cls.can_transition(order.status, new_status):
            logger.warning(f"Invalid transition: {order.status} -> {new_status} for order {order.id}")
            return False
        
        old_status = order.status
        order.status = new_status
        
        # Update timestamps
        if new_status == OrderStatus.SUBMITTED:
            order.submitted_at = datetime.utcnow()
        elif new_status == OrderStatus.FILLED:
            order.filled_at = datetime.utcnow()
        
        # Store rejection reason
        if new_status == OrderStatus.REJECTED and reason:
            order.rejection_reason = reason
        
        logger.info(f"Order {order.id} transitioned: {old_status} -> {new_status}")
        return True
    
    @classmethod
    def add_fill(cls, order: Order, quantity: int, price: float) -> None:
        """
        Add fill to order
        
        Args:
            order: Order instance
            quantity: Filled quantity
            price: Fill price
        """
        fill = {
            "quantity": quantity,
            "price": float(price),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not isinstance(order.fills, list):
            order.fills = []
        
        order.fills.append(fill)
        order.filled_quantity += quantity
        
        # Calculate average fill price
        total_value = sum(f["quantity"] * f["price"] for f in order.fills)
        order.average_fill_price = total_value / order.filled_quantity
        
        # Update status
        if order.filled_quantity >= order.quantity:
            cls.transition(order, OrderStatus.FILLED)
        elif order.filled_quantity > 0:
            cls.transition(order, OrderStatus.PARTIALLY_FILLED)
        
        logger.info(f"Order {order.id} filled: {quantity} @ {price} (total: {order.filled_quantity}/{order.quantity})")
