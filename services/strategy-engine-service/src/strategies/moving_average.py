"""
Moving Average Crossover Strategy
VELOX Trading Platform
"""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import pandas as pd
import numpy as np

from .base import StrategyBase


class MovingAverageCrossover(StrategyBase):
    """
    Moving Average Crossover Strategy
    
    Generates buy signal when short MA crosses above long MA
    Generates sell signal when short MA crosses below long MA
    """
    
    def initialize(self) -> None:
        """Initialize strategy parameters"""
        self.short_window = self.config.get("short_window", 10)
        self.long_window = self.config.get("long_window", 30)
        self.rsi_period = self.config.get("rsi_period", 14)
        self.rsi_oversold = self.config.get("rsi_oversold", 30)
        self.rsi_overbought = self.config.get("rsi_overbought", 70)
        
        # Validate parameters
        if self.short_window >= self.long_window:
            raise ValueError("Short window must be less than long window")
    
    def on_tick(self, instrument_id: UUID, tick: dict[str, Any]) -> None:
        """Process new market data tick"""
        # Initialize DataFrame for instrument if not exists
        if instrument_id not in self.market_data:
            self.market_data[instrument_id] = pd.DataFrame(columns=['timestamp', 'price', 'volume'])
        
        # Append new tick
        new_row = pd.DataFrame([{
            'timestamp': tick['timestamp'],
            'price': float(tick['price']),
            'volume': tick['volume']
        }])
        self.market_data[instrument_id] = pd.concat(
            [self.market_data[instrument_id], new_row],
            ignore_index=True
        )
        
        # Keep only last 200 ticks (for performance)
        if len(self.market_data[instrument_id]) > 200:
            self.market_data[instrument_id] = self.market_data[instrument_id].iloc[-200:]
    
    def calculate_signals(self, instrument_id: UUID) -> Optional[dict[str, Any]]:
        """Calculate trading signals"""
        if instrument_id not in self.market_data:
            return None
        
        df = self.market_data[instrument_id]
        
        # Need enough data for long MA
        if len(df) < self.long_window + 1:
            return None
        
        # Calculate moving averages
        df['sma_short'] = df['price'].rolling(window=self.short_window).mean()
        df['sma_long'] = df['price'].rolling(window=self.long_window).mean()
        
        # Calculate RSI
        df['rsi'] = self._calculate_rsi(df['price'], self.rsi_period)
        
        # Get last two rows for crossover detection
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # Check for crossover
        signal = None
        
        # Bullish crossover (short MA crosses above long MA) + RSI oversold
        if (previous['sma_short'] <= previous['sma_long'] and 
            current['sma_short'] > current['sma_long'] and
            current['rsi'] < self.rsi_oversold):
            
            signal = {
                "signal_type": "ENTRY_LONG",
                "strength": min((self.rsi_oversold - current['rsi']) / self.rsi_oversold, 1.0),
                "indicators": {
                    "sma_short": float(current['sma_short']),
                    "sma_long": float(current['sma_long']),
                    "rsi": float(current['rsi'])
                },
                "reasoning": f"SMA short ({self.short_window}) crossed above SMA long ({self.long_window}) with RSI oversold",
                "recommended_quantity": 1,  # Will be calculated by position sizing
                "recommended_price": float(current['price'])
            }
        
        # Bearish crossover (short MA crosses below long MA) + RSI overbought
        elif (previous['sma_short'] >= previous['sma_long'] and 
              current['sma_short'] < current['sma_long'] and
              current['rsi'] > self.rsi_overbought):
            
            signal = {
                "signal_type": "ENTRY_SHORT",
                "strength": min((current['rsi'] - self.rsi_overbought) / (100 - self.rsi_overbought), 1.0),
                "indicators": {
                    "sma_short": float(current['sma_short']),
                    "sma_long": float(current['sma_long']),
                    "rsi": float(current['rsi'])
                },
                "reasoning": f"SMA short ({self.short_window}) crossed below SMA long ({self.long_window}) with RSI overbought",
                "recommended_quantity": 1,
                "recommended_price": float(current['price'])
            }
        
        return signal
    
    def manage_positions(self, instrument_id: UUID, current_price: float) -> Optional[dict[str, Any]]:
        """Manage existing positions"""
        if instrument_id not in self.positions:
            return None
        
        position = self.positions[instrument_id]
        df = self.market_data.get(instrument_id)
        
        if df is None or len(df) < 2:
            return None
        
        current = df.iloc[-1]
        
        # Exit long position if short MA crosses below long MA
        if position['side'] == 'LONG':
            if current['sma_short'] < current['sma_long']:
                return {
                    "signal_type": "EXIT_LONG",
                    "strength": 0.8,
                    "indicators": {
                        "sma_short": float(current['sma_short']),
                        "sma_long": float(current['sma_long'])
                    },
                    "reasoning": "SMA short crossed below SMA long - exit long position",
                    "recommended_quantity": position['quantity'],
                    "recommended_price": current_price
                }
        
        # Exit short position if short MA crosses above long MA
        elif position['side'] == 'SHORT':
            if current['sma_short'] > current['sma_long']:
                return {
                    "signal_type": "EXIT_SHORT",
                    "strength": 0.8,
                    "indicators": {
                        "sma_short": float(current['sma_short']),
                        "sma_long": float(current['sma_long'])
                    },
                    "reasoning": "SMA short crossed above SMA long - exit short position",
                    "recommended_quantity": position['quantity'],
                    "recommended_price": current_price
                }
        
        return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
