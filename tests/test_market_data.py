"""Tests for MarketData class."""
import pytest
from src.data.market_data import MarketData, BarData, TickData

def test_bar_data_creation():
    """Test BarData object creation."""
    bar = BarData(
        symbol="AAPL",
        datetime="2023-01-01 09:30:00",
        open=150.0,
        high=152.0,
        low=149.5,
        close=151.0,
        volume=100000
    )
    assert bar.symbol == "AAPL"
    assert bar.open == 150.0

def test_tick_data_creation():
    """Test TickData object creation."""
    tick = TickData(
        symbol="AAPL",
        datetime="2023-01-01 09:30:01",
        price=151.0,
        volume=100
    )
    assert tick.symbol == "AAPL"
    assert tick.price == 151.0