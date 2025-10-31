"""
Signal Generator
VELOX Trading Platform
"""
import logging
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from .strategies.base import StrategyBase

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generate trading signals from strategy logic"""
    
    def __init__(self, strategy: StrategyBase):
        self.strategy = strategy
    
    def generate_signal(self, instrument_id: UUID, symbol: str) -> Optional[dict[str, Any]]:
        """
        Generate trading signal for instrument
        
        Args:
            instrument_id: Instrument identifier
            symbol: Instrument symbol
        
        Returns:
            Signal event dictionary or None
        """
        try:
            # Calculate signal from strategy
            signal = self.strategy.calculate_signals(instrument_id)
            
            if signal is None:
                return None
            
            # Enrich signal with metadata
            signal_event = {
                "signal_id": str(uuid4()),
                "strategy_id": str(self.strategy.strategy_id),
                "strategy_name": self.strategy.__class__.__name__,
                "instrument_id": str(instrument_id),
                "symbol": symbol,
                "signal_type": signal["signal_type"],
                "strength": signal["strength"],
                "indicators": signal["indicators"],
                "reasoning": signal["reasoning"],
                "recommended_quantity": signal["recommended_quantity"],
                "recommended_price": signal["recommended_price"],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Signal generated: {signal_event['signal_type']} for {symbol} (strength: {signal['strength']:.2f})")
            return signal_event
        
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}", exc_info=True)
            return None
    
    def check_exit_conditions(self, instrument_id: UUID, symbol: str, current_price: float) -> Optional[dict[str, Any]]:
        """
        Check if existing position should be exited
        
        Args:
            instrument_id: Instrument identifier
            symbol: Instrument symbol
            current_price: Current market price
        
        Returns:
            Exit signal event or None
        """
        try:
            exit_signal = self.strategy.manage_positions(instrument_id, current_price)
            
            if exit_signal is None:
                return None
            
            # Enrich exit signal
            signal_event = {
                "signal_id": str(uuid4()),
                "strategy_id": str(self.strategy.strategy_id),
                "strategy_name": self.strategy.__class__.__name__,
                "instrument_id": str(instrument_id),
                "symbol": symbol,
                "signal_type": exit_signal["signal_type"],
                "strength": exit_signal["strength"],
                "indicators": exit_signal["indicators"],
                "reasoning": exit_signal["reasoning"],
                "recommended_quantity": exit_signal["recommended_quantity"],
                "recommended_price": exit_signal["recommended_price"],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Exit signal generated: {signal_event['signal_type']} for {symbol}")
            return signal_event
        
        except Exception as e:
            logger.error(f"Error checking exit conditions for {symbol}: {e}", exc_info=True)
            return None
