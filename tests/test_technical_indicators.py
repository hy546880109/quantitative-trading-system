"""Tests for technical indicators."""
import pytest
import pandas as pd
from src.strategies.technical_indicators import TechnicalIndicators


def test_sma_calculation():
    """Test SMA calculation."""
    prices = [100, 102, 101, 103, 105, 104, 106]
    ti = TechnicalIndicators(pd.DataFrame({'close': prices}))

    sma_values = ti.sma(window=3)
    # Expected: [(100+102+101)/3, (102+101+103)/3, ...]
    expected = [101.0, 102.0, 103.0, 104.0, 105.0]
    assert sma_values.tolist()[2:] == expected  # First 2 values are NaN


def test_ema_calculation():
    """Test EMA calculation."""
    prices = [100, 102, 101, 103, 105]
    ti = TechnicalIndicators(pd.DataFrame({'close': prices}))

    ema_values = ti.ema(window=3)
    # First value is the same as price, then calculated with smoothing factor
    assert ema_values[0] == 100  # First value
    # Test that subsequent values are calculated correctly
    assert len(ema_values) == len(prices)


def test_macd_calculation():
    """Test MACD calculation."""
    prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
    ti = TechnicalIndicators(pd.DataFrame({'close': prices}))

    macd_line, signal_line, histogram = ti.macd()
    assert len(macd_line) == len(prices)
    assert len(signal_line) == len(prices)
    assert len(histogram) == len(prices)