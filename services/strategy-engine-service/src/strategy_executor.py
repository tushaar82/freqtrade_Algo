"""
Strategy Executor - Orchestrates Strategy Execution
VELOX Trading Platform
"""
import asyncio
import logging
from typing import Any
from uuid import UUID

from .strategy_loader import StrategyLoader
from .signal_generator import SignalGenerator
from .kafka_consumer import MarketDataConsumer
from .kafka_producer import SignalEventProducer
from .config import settings

logger = logging.getLogger(__name__)


class StrategyExecutor:
    """Orchestrate strategy execution and signal generation"""
    
    def __init__(self):
        self.strategy_loader = StrategyLoader(settings.STRATEGY_DIR)
        self.active_strategies: dict[UUID, tuple[Any, SignalGenerator]] = {}
        self.signal_producer = SignalEventProducer()
        self.market_data_consumer = None
        self.running = False
    
    async def run(self) -> None:
        """Start strategy executor"""
        self.running = True
        logger.info("Strategy executor started")
        
        # Start market data consumer in background
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self._start_market_data_consumer)
    
    def _start_market_data_consumer(self) -> None:
        """Start consuming market data"""
        self.market_data_consumer = MarketDataConsumer(self._on_market_tick)
        self.market_data_consumer.start()
    
    def _on_market_tick(self, event: dict[str, Any]) -> None:
        """
        Process market data tick
        
        Args:
            event: Market tick event from Kafka
        """
        try:
            payload = event.get("payload", {})
            instrument_id = UUID(payload["instrument_id"])
            symbol = payload["symbol"]
            
            # Process tick for all active strategies
            for strategy_id, (strategy, signal_gen) in self.active_strategies.items():
                # Update strategy with new tick
                strategy.on_tick(instrument_id, payload)
                
                # Generate entry signals
                signal = signal_gen.generate_signal(instrument_id, symbol)
                if signal:
                    self.signal_producer.publish_signal(signal)
                
                # Check exit conditions for existing positions
                if instrument_id in strategy.positions:
                    current_price = float(payload["price"])
                    exit_signal = signal_gen.check_exit_conditions(instrument_id, symbol, current_price)
                    if exit_signal:
                        self.signal_producer.publish_signal(exit_signal)
        
        except Exception as e:
            logger.error(f"Error processing market tick: {e}", exc_info=True)
    
    def activate_strategy(self, strategy_id: UUID, strategy_type: str, config: dict[str, Any]) -> None:
        """
        Activate a trading strategy
        
        Args:
            strategy_id: Strategy identifier
            strategy_type: Strategy class name
            config: Strategy configuration
        """
        try:
            strategy = self.strategy_loader.create_strategy(strategy_id, strategy_type, config)
            signal_gen = SignalGenerator(strategy)
            self.active_strategies[strategy_id] = (strategy, signal_gen)
            logger.info(f"Activated strategy: {strategy_type} ({strategy_id})")
        except Exception as e:
            logger.error(f"Failed to activate strategy {strategy_id}: {e}")
            raise
    
    def deactivate_strategy(self, strategy_id: UUID) -> None:
        """
        Deactivate a trading strategy
        
        Args:
            strategy_id: Strategy identifier
        """
        if strategy_id in self.active_strategies:
            strategy, _ = self.active_strategies[strategy_id]
            strategy.cleanup()
            del self.active_strategies[strategy_id]
            logger.info(f"Deactivated strategy: {strategy_id}")
    
    async def stop(self) -> None:
        """Stop strategy executor"""
        self.running = False
        logger.info("Stopping strategy executor...")
        
        # Deactivate all strategies
        for strategy_id in list(self.active_strategies.keys()):
            self.deactivate_strategy(strategy_id)
        
        # Close producers/consumers
        if self.market_data_consumer:
            self.market_data_consumer.stop()
        self.signal_producer.close()
        
        logger.info("Strategy executor stopped")
