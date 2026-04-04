#!/usr/bin/env python3
"""
量化交易系统主入口
用法: python main.py
"""
import sys
import pandas as pd
from src.data.market_data import BarData, MarketData
from src.data.data_feed import DataFeed
from src.strategies.technical_indicators import (
    TechnicalIndicators,
    MovingAverageStrategy,
    RSIStrategy
)
from src.core.backtest_engine import BacktestEngine


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_data_structures():
    """演示数据结构"""
    print_header("1. 数据结构演示")

    # K线数据
    bar = BarData(
        symbol="000001.SZ",
        datetime="2024-01-01",
        open=10.5,
        high=11.0,
        low=10.2,
        close=10.8,
        volume=1000000
    )
    print(f"K线数据: {bar.symbol} @ {bar.datetime}")
    print(f"  开盘: {bar.open}, 最高: {bar.high}, 最低: {bar.low}, 收盘: {bar.close}")

    # 市场数据管理
    market = MarketData()
    for i in range(5):
        bar = BarData(
            symbol="000001.SZ",
            datetime=f"2024-01-0{i+1}",
            open=10.0 + i,
            high=11.0 + i,
            low=9.0 + i,
            close=10.5 + i,
            volume=1000000 + i * 10000
        )
        market.add_bar(bar)

    latest = market.get_latest_bar("000001.SZ")
    print(f"最新K线: {latest.datetime}, 收盘价: {latest.close}")


def demo_indicators():
    """演示技术指标"""
    print_header("2. 技术指标演示")

    # 生成模拟数据
    import numpy as np
    dates = pd.date_range('2024-01-01', periods=50, freq='D')
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(50) * 2)

    data = pd.DataFrame({
        'open': prices + np.random.randn(50) * 0.5,
        'high': prices + np.abs(np.random.randn(50)) * 2,
        'low': prices - np.abs(np.random.randn(50)) * 2,
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, 50)
    }, index=dates)

    ti = TechnicalIndicators(data)

    print(f"SMA(5):  {ti.sma(5).iloc[-1]:.2f}")
    print(f"SMA(20): {ti.sma(20).iloc[-1]:.2f}")
    print(f"EMA(12): {ti.ema(12).iloc[-1]:.2f}")
    print(f"RSI(14): {ti.rsi(14).iloc[-1]:.2f}")
    print(f"MACD:    {ti.macd()[0].iloc[-1]:.2f}")
    print(f"ATR(14): {ti.atr(14).iloc[-1]:.2f}")

    upper, middle, lower = ti.bbands(20)
    print(f"布林带: {lower.iloc[-1]:.2f} ~ {middle.iloc[-1]:.2f} ~ {upper.iloc[-1]:.2f}")


def demo_strategies():
    """演示交易策略"""
    print_header("3. 交易策略演示")

    # 准备历史数据
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    import numpy as np
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 2)

    data = pd.DataFrame({
        'open': prices + np.random.randn(100) * 0.5,
        'high': prices + np.abs(np.random.randn(100)) * 2,
        'low': prices - np.abs(np.random.randn(100)) * 2,
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, 100)
    }, index=dates)

    # 均线策略
    ma_strategy = MovingAverageStrategy(short_window=10, long_window=30)
    ma_signals = ma_strategy.generate_signals(data)

    # RSI策略
    rsi_strategy = RSIStrategy(window=14, oversold=30, overbought=70)
    rsi_signals = rsi_strategy.generate_signals(data)

    print("均线策略信号统计:")
    print(f"  买入信号: {(ma_signals == 1).sum()}")
    print(f"  卖出信号: {(ma_signals == -1).sum()}")
    print(f"  持有信号: {(ma_signals == 0).sum()}")

    print("\nRSI策略信号统计:")
    print(f"  买入信号: {(rsi_signals == 1).sum()}")
    print(f"  卖出信号: {(rsi_signals == -1).sum()}")
    print(f"  持有信号: {(rsi_signals == 0).sum()}")


def demo_backtest():
    """演示完整回测"""
    print_header("4. 完整回测演示")

    # 准备历史数据
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    import numpy as np
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(200) * 2)

    data = pd.DataFrame({
        'open': prices + np.random.randn(200) * 0.5,
        'high': prices + np.abs(np.random.randn(200)) * 2,
        'low': prices - np.abs(np.random.randn(200)) * 2,
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, 200)
    }, index=dates)

    # 创建策略和回测引擎
    strategy = MovingAverageStrategy(short_window=10, long_window=30)
    engine = BacktestEngine(initial_capital=100000)

    # 运行回测
    result = engine.run_backtest(strategy, data, symbol="000001.SZ")

    # 打印结果
    print(f"\n初始资金: ¥{result['initial_capital']:,.2f}")
    print(f"最终价值: ¥{result['final_value']:,.2f}")
    print(f"总收益率: {result['total_return_pct']:.2f}%")
    print(f"夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"最大回撤: {result['max_drawdown']:.2f}%")
    print(f"总交易次数: {result['total_trades']}")
    print(f"买入次数: {result['buy_trades']}")
    print(f"卖出次数: {result['sell_trades']}")

    # 显示交易记录
    if result['trades']:
        print("\n交易记录:")
        for i, trade in enumerate(result['trades'][:5], 1):
            print(f"  {i}. {trade['date'][:10]} | {trade['action']:4} | "
                  f"数量:{trade['quantity']:4} | 价格:¥{trade['price']:.2f} | "
                  f"总额:¥{trade['total']:,.2f}")
        if len(result['trades']) > 5:
            print(f"  ... 还有 {len(result['trades']) - 5} 笔交易")


def demo_tushare():
    """演示TuShare数据获取（需要有效token）"""
    print_header("5. TuShare数据获取演示")

    print("提示: TuShare需要有效token才能获取真实数据")
    print("用法示例:")
    print("  from src.data.data_feed import DataFeed")
    print("  feed = DataFeed.create('tushare', token='your_token_here')")
    print("  data = feed.fetch_daily_data('000001.SZ', '20240101', '20241201')")


def main():
    """主函数"""
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#    量化交易系统 v1.0                               #")
    print("#" + " " * 58 + "#")
    print("#" * 60)

    try:
        # 1. 数据结构
        demo_data_structures()

        # 2. 技术指标
        demo_indicators()

        # 3. 交易策略
        demo_strategies()

        # 4. 完整回测
        demo_backtest()

        # 5. TuShare（信息展示）
        demo_tushare()

        # 完成
        print_header("系统演示完成")
        print("\n如需获取真实数据，请使用TuShare接口:")
        print("  feed = DataFeed.create('tushare', token='your_token')")
        print("  data = feed.fetch_daily_data('000001.SZ', '20240101', '20241201')")
        print()

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
