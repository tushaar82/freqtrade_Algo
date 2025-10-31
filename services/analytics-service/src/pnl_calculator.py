"""
P&L Calculator
VELOX Trading Platform
"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PnLCalculator:
    """Calculate P&L metrics"""
    
    def __init__(self):
        self.strategy_pnl: Dict[str, Dict] = {}
    
    def update_position_pnl(self, position: dict):
        """Update P&L for position"""
        strategy_id = position["strategy_id"]
        
        if strategy_id not in self.strategy_pnl:
            self.strategy_pnl[strategy_id] = {
                "realized_pnl": 0.0,
                "unrealized_pnl": 0.0,
                "total_pnl": 0.0,
                "daily_pnl": 0.0,
                "positions": {}
            }
        
        # Update unrealized P&L
        position_id = position["position_id"]
        self.strategy_pnl[strategy_id]["positions"][position_id] = position["unrealized_pnl"]
        
        # Recalculate totals
        unrealized = sum(self.strategy_pnl[strategy_id]["positions"].values())
        realized = self.strategy_pnl[strategy_id]["realized_pnl"]
        
        self.strategy_pnl[strategy_id]["unrealized_pnl"] = unrealized
        self.strategy_pnl[strategy_id]["total_pnl"] = realized + unrealized
    
    def update_trade_pnl(self, trade: dict):
        """Update P&L for closed trade"""
        strategy_id = trade["strategy_id"]
        
        if strategy_id not in self.strategy_pnl:
            self.strategy_pnl[strategy_id] = {
                "realized_pnl": 0.0,
                "unrealized_pnl": 0.0,
                "total_pnl": 0.0,
                "daily_pnl": 0.0,
                "positions": {}
            }
        
        # Add realized P&L
        net_pnl = trade.get("net_pnl", 0.0)
        self.strategy_pnl[strategy_id]["realized_pnl"] += net_pnl
        self.strategy_pnl[strategy_id]["total_pnl"] += net_pnl
        
        # Remove from unrealized
        position_id = trade.get("position_id")
        if position_id in self.strategy_pnl[strategy_id]["positions"]:
            del self.strategy_pnl[strategy_id]["positions"][position_id]
    
    def get_strategy_pnl(self, strategy_id: str) -> dict:
        """Get P&L for strategy"""
        return self.strategy_pnl.get(strategy_id, {
            "realized_pnl": 0.0,
            "unrealized_pnl": 0.0,
            "total_pnl": 0.0,
            "daily_pnl": 0.0
        })
    
    def get_total_pnl(self) -> dict:
        """Get total P&L across all strategies"""
        total_realized = sum(s["realized_pnl"] for s in self.strategy_pnl.values())
        total_unrealized = sum(s["unrealized_pnl"] for s in self.strategy_pnl.values())
        
        return {
            "realized_pnl": total_realized,
            "unrealized_pnl": total_unrealized,
            "total_pnl": total_realized + total_unrealized
        }
