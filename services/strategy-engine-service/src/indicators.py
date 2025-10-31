"""
Technical Indicators
VELOX Trading Platform
"""
import pandas as pd
import numpy as np


def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average
    
    Args:
        prices: Price series
        period: Moving average period
    
    Returns:
        SMA series
    """
    return prices.rolling(window=period).mean()


def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average
    
    Args:
        prices: Price series
        period: Moving average period
    
    Returns:
        EMA series
    """
    return prices.ewm(span=period, adjust=False).mean()


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index
    
    Args:
        prices: Price series
        period: RSI period (default 14)
    
    Returns:
        RSI series (0-100)
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: Price series
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period
    
    Returns:
        Tuple of (MACD line, Signal line, Histogram)
    """
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands
    
    Args:
        prices: Price series
        period: Moving average period
        std_dev: Number of standard deviations
    
    Returns:
        Tuple of (Upper band, Middle band, Lower band)
    """
    middle_band = calculate_sma(prices, period)
    std = prices.rolling(window=period).std()
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return upper_band, middle_band, lower_band


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range
    
    Args:
        high: High price series
        low: Low price series
        close: Close price series
        period: ATR period
    
    Returns:
        ATR series
    """
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr
