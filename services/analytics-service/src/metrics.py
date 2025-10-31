"""
Performance Metrics Calculator
VELOX Trading Platform
"""
import numpy as np
import pandas as pd
from typing import List


class MetricsCalculator:
    """Calculate trading performance metrics"""
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe Ratio"""
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate
        
        if np.std(excess_returns) == 0:
            return 0.0
        
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)  # Annualized
    
    def calculate_sortino_ratio(self, returns: List[float], risk_free_rate: float = 0.0) -> float:
        """Calculate Sortino Ratio (downside deviation)"""
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate
        
        # Only consider negative returns for downside deviation
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or np.std(downside_returns) == 0:
            return 0.0
        
        downside_deviation = np.std(downside_returns)
        return np.mean(excess_returns) / downside_deviation * np.sqrt(252)
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Calculate Maximum Drawdown"""
        if not equity_curve or len(equity_curve) < 2:
            return 0.0
        
        equity_array = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max
        
        return float(np.min(drawdown))
    
    def calculate_calmar_ratio(self, returns: List[float], equity_curve: List[float]) -> float:
        """Calculate Calmar Ratio (return / max drawdown)"""
        if not returns or not equity_curve:
            return 0.0
        
        annual_return = np.mean(returns) * 252
        max_dd = abs(self.calculate_max_drawdown(equity_curve))
        
        if max_dd == 0:
            return 0.0
        
        return annual_return / max_dd
    
    def calculate_win_rate(self, trades: List[dict]) -> float:
        """Calculate win rate"""
        if not trades:
            return 0.0
        
        winning_trades = sum(1 for t in trades if t.get("net_pnl", 0) > 0)
        return winning_trades / len(trades)
    
    def calculate_profit_factor(self, trades: List[dict]) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        if not trades:
            return 0.0
        
        gross_profit = sum(t.get("net_pnl", 0) for t in trades if t.get("net_pnl", 0) > 0)
        gross_loss = abs(sum(t.get("net_pnl", 0) for t in trades if t.get("net_pnl", 0) < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
