"""Stop Loss Manager"""
import logging

logger = logging.getLogger(__name__)

class StopLossManager:
    def calculate_fixed_stop_loss(self, entry_price: float, side: str, stop_loss_percent: float) -> float:
        if side == "LONG":
            return entry_price * (1 - stop_loss_percent / 100)
        else:
            return entry_price * (1 + stop_loss_percent / 100)
    
    def calculate_trailing_stop_loss(self, current_price: float, side: str, trailing_percent: float, current_stop: float = None) -> float:
        new_stop = current_price * (1 - trailing_percent / 100) if side == "LONG" else current_price * (1 + trailing_percent / 100)
        
        if current_stop is None:
            return new_stop
        
        if side == "LONG":
            return max(new_stop, current_stop)
        else:
            return min(new_stop, current_stop)
    
    def is_stop_loss_hit(self, current_price: float, stop_loss_price: float, side: str) -> bool:
        if side == "LONG":
            return current_price <= stop_loss_price
        else:
            return current_price >= stop_loss_price
