"""
Base Strategy Class
VELOX Trading Platform
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import pandas as pd


class StrategyBase(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, strategy_id: UUID, config: dict[str, Any]):
        """
        Initialize strategy
        
        Args:
            strategy_id: Unique strategy identifier
            config: Strategy configuration parameters
        """
        self.strategy_id = strategy_id
        self.config = config
        self.market_data: dict[UUID, pd.DataFrame] = {}  # instrument_id -> OHLCV DataFrame
        self.positions: dict[UUID, dict] = {}  # instrument_id -> position details
        self.indicators: dict[str, Any] = {}
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize strategy (load indicators, set parameters)"""
        pass
    
    @abstractmethod
    def on_tick(self, instrument_id: UUID, tick: dict[str, Any]) -> None:
        """
        Process new market data tick
        
        Args:
            instrument_id: Instrument identifier
            tick: Market data tick (price, volume, timestamp)
        """
        pass
    
    @abstractmethod
    def calculate_signals(self, instrument_id: UUID) -> Optional[dict[str, Any]]:
        """
        Calculate trading signals for instrument
        
        Args:
            instrument_id: Instrument identifier
        
        Returns:
            Signal dictionary or None if no signal
            {
                "signal_type": "ENTRY_LONG" | "ENTRY_SHORT" | "EXIT_LONG" | "EXIT_SHORT",
                "strength": float (0.0 to 1.0),
                "indicators": dict,
                "reasoning": str,
                "recommended_quantity": int,
                "recommended_price": float
            }
        """
        pass
    
    @abstractmethod
    def manage_positions(self, instrument_id: UUID, current_price: float) -> Optional[dict[str, Any]]:
        """
        Manage existing positions (update stop-loss, check exit conditions)
        
        Args:
            instrument_id: Instrument identifier
            current_price: Current market price
        
        Returns:
            Exit signal dictionary or None
        """
        pass
    
    def cleanup(self) -> None:
        """Cleanup resources (optional override)"""
        pass
    
    def get_metadata(self) -> dict[str, Any]:
        """
        Get strategy metadata
        
        Returns:
            Metadata dictionary with name, description, parameters
        """
        return {
            "name": self.__class__.__name__,
            "description": self.__doc__ or "No description",
            "parameters": self.config
        }
