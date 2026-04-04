"""Tests for backtest engine."""
import pytest
import pandas as pd
from src.core.backtest_engine import BacktestEngine
from src.strategies.technical_indicators import MovingAverageStrategy


def test_backtest_engine_initialization():
    """Test BacktestEngine initialization."""
    engine = BacktestEngine(initial_capital=10000)
    assert engine.initial_capital == 10000
    assert engine.current_capital == 10000
    assert len(engine.portfolio) == 0


def test_backtest_execution():
    """Test backtest execution with sample data."""
    # Create sample data
    data = pd.DataFrame({
        'close': [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
        'high': [101, 103, 102, 104, 106, 105, 107, 109, 108, 110],
        'low': [99, 101, 100, 102, 104, 103, 105, 107, 106, 108]
    })

    strategy = MovingAverageStrategy(short_window=3, long_window=5)
    engine = BacktestEngine(initial_capital=10000)

    results = engine.run_backtest(strategy, data)

    # Check that results include necessary metrics
    assert 'total_return' in results
    assert 'sharpe_ratio' in results
    assert 'max_drawdown' in results
    assert isinstance(results['total_return'], float)