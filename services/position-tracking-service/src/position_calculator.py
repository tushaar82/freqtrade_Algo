"""Position P&L Calculator"""
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class PositionCalculator:
    def calculate_unrealized_pnl(self, side: str, quantity: int, entry_price: float, current_price: float) -> float:
        if side == "LONG":
            return quantity * (current_price - entry_price)
        else:  # SHORT
            return quantity * (entry_price - current_price)
    
    def calculate_realized_pnl(self, side: str, quantity: int, entry_price: float, exit_price: float, transaction_costs: float = 0) -> tuple[float, float]:
        if side == "LONG":
            gross_pnl = quantity * (exit_price - entry_price)
        else:
            gross_pnl = quantity * (entry_price - exit_price)
        
        net_pnl = gross_pnl - transaction_costs
        return gross_pnl, net_pnl
