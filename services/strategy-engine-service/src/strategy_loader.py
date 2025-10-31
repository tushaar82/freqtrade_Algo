"""
Strategy Loader - Dynamic Strategy Discovery
VELOX Trading Platform
"""
import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, Type
from uuid import UUID

from .strategies.base import StrategyBase

logger = logging.getLogger(__name__)


class StrategyLoader:
    """Dynamically load and instantiate trading strategies"""
    
    def __init__(self, strategy_dir: str = "./src/strategies"):
        self.strategy_dir = Path(strategy_dir)
        self.strategies: dict[str, Type[StrategyBase]] = {}
        self._discover_strategies()
    
    def _discover_strategies(self) -> None:
        """Discover all strategy classes in strategies directory"""
        logger.info(f"Discovering strategies in {self.strategy_dir}")
        
        if not self.strategy_dir.exists():
            logger.warning(f"Strategy directory not found: {self.strategy_dir}")
            return
        
        for file_path in self.strategy_dir.glob("*.py"):
            if file_path.name.startswith("_") or file_path.name == "base.py":
                continue
            
            try:
                module_name = f"src.strategies.{file_path.stem}"
                module = importlib.import_module(module_name)
                
                # Find strategy classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, StrategyBase) and 
                        obj is not StrategyBase and
                        obj.__module__ == module_name):
                        
                        self.strategies[name] = obj
                        logger.info(f"Loaded strategy: {name}")
            
            except Exception as e:
                logger.error(f"Failed to load strategy from {file_path}: {e}")
    
    def get_strategy_class(self, strategy_type: str) -> Type[StrategyBase]:
        """Get strategy class by type name"""
        if strategy_type not in self.strategies:
            raise ValueError(f"Strategy type not found: {strategy_type}")
        return self.strategies[strategy_type]
    
    def create_strategy(self, strategy_id: UUID, strategy_type: str, config: dict[str, Any]) -> StrategyBase:
        """Create strategy instance"""
        strategy_class = self.get_strategy_class(strategy_type)
        strategy = strategy_class(strategy_id, config)
        strategy.initialize()
        return strategy
    
    def list_strategies(self) -> list[str]:
        """List all available strategy types"""
        return list(self.strategies.keys())
