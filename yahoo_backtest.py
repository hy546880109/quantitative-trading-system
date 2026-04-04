"""
使用Yahoo Finance数据回测（无需token）
支持A股、港股、美股
用法: python yahoo_backtest.py [--years 3]
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import datetime, timedelta
from src.data.data_feed import DataFeed
from src.strategies.technical_indicators import (
    MovingAverageStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy,
    KDJStrategy,
    EMAStrategy,
    CombinedStrategy
)
from src.core.backtest_engine import BacktestEngine


def bars_to_dataframe(bars):
    """将BarData列表转换为DataFrame，按日期正序排列"""
    if not bars:
        return pd.DataFrame()

    # 按日期排序（正序：从早到晚）
    bars = sorted(bars, key=lambda x: x.datetime)

    data = {
        'open': [bar.open for bar in bars],
        'high': [bar.high for bar in bars],
        'low': [bar.low for bar in bars],
        'close': [bar.close for bar in bars],
        'volume': [bar.volume for bar in bars]
    }
    index = [bar.datetime for bar in bars]
    return pd.DataFrame(data, index=index)


def run_strategy(name, strategy, data, symbol):
    """运行单个策略并返回结果"""
    engine = BacktestEngine(initial_capital=100000)
    result = engine.run_backtest(strategy, data, symbol=symbol)
    return {
        'name': name,
        'return': result['total_return_pct'],
        'sharpe': result['sharpe_ratio'],
        'drawdown': result['max_drawdown'],
        'trades': result['total_trades'],
        'final_value': result['final_value']
    }


def convert_symbol(symbol: str) -> str:
    """转换为Yahoo Finance支持的指数代码"""
    # 指数代码映射
    index_mapping = {
        # 美股指数
        "IXIC": "^IXIC",      # 纳斯达克指数
        "GSPC": "^GSPC",      # 标普500
        "DJI": "^DJI",        # 道琼斯
        # A股指数
        "000001.SH": "000001.SS",  # 上证指数 (Yahoo使用.SS后缀)
        "399001.SZ": "399001.SZ",  # 深证成指
        "399006.SZ": "399006.SZ",  # 创业板指
        "000300.SH": "000300.SS",  # 沪深300
        "000016.SH": "000016.SS",  # 上证50
    }

    # 检查是否是指数代码
    if symbol in index_mapping:
        return index_mapping[symbol]

    # 股票代码转换
    if symbol.endswith('.SH'):
        return symbol.replace('.SH', '.SS')
    return symbol


def run_yahoo_backtest(years=3):
    """使用Yahoo Finance数据运行回测

    Args:
        years: 回测年数，默认3年
    """

    # 检查yfinance是否安装
    try:
        import yfinance
    except ImportError:
        print("=" * 60)
        print("请先安装yfinance:")
        print("  pip install yfinance")
        print("=" * 60)
        return

    # 创建数据源（无需token）
    print("正在连接Yahoo Finance数据源...")
    feed = DataFeed("yahoo", token=None)

    # 设置回测参数（5年）
    symbols = [
        # 美股指数
        ("IXIC", "纳斯达克指数"),
        ("GSPC", "标普500"),
        ("DJI", "道琼斯"),
        # A股指数（Yahoo Finance支持的）
        ("000001.SH", "上证指数"),
        ("399001.SZ", "深证成指"),
        ("000300.SH", "沪深300"),
        # 个股
        ("000001.SZ", "平安银行"),
        ("600519.SH", "贵州茅台"),
        ("AAPL", "苹果"),
        ("GOOGL", "谷歌"),
    ]

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)  # 动态计算年数

    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')

    for symbol, name in symbols:
        print(f"\n{'=' * 70}")
        print(f"股票: {name} ({symbol})")
        print(f"{'=' * 70}")

        # 获取数据（使用转换后的代码）
        yahoo_symbol = convert_symbol(symbol)
        bars = feed.fetch_daily_data(yahoo_symbol, start_date_str, end_date_str)

        if not bars:
            print(f"获取 {symbol} 数据失败，跳过")
            continue

        print(f"成功获取 {len(bars)} 条K线数据")

        # 转换为DataFrame
        data = bars_to_dataframe(bars)

        # 显示数据概览
        print(f"\n数据概览:")
        print(f"  起始日期: {data.index[0]}")
        print(f"  结束日期: {data.index[-1]}")
        print(f"  最高价格: ¥{data['high'].max():.2f}")
        print(f"  最低价格: ¥{data['low'].min():.2f}")
        print(f"  最新收盘: ¥{data['close'].iloc[-1]:.2f}")

        # 判断是否为指数
        index_symbols = {"IXIC", "GSPC", "DJI", "000001.SH", "399001.SZ", "000300.SH"}
        is_index = symbol in index_symbols

        # 根据标的类型选择策略参数
        if is_index:
            # 指数参数：更长周期、更宽阈值，适合趋势跟踪
            strategies = [
                ("均线策略(SMA)", MovingAverageStrategy(short_window=10, long_window=30)),
                ("RSI策略", RSIStrategy(window=21, oversold=25, overbought=75)),
                ("MACD策略", MACDStrategy(fast=8, slow=21, signal=5)),
                ("布林带策略", BollingerBandsStrategy(window=20, num_std=1.5)),
                ("KDJ策略", KDJStrategy(k_window=21, d_window=5, oversold=15, overbought=85)),
                ("EMA策略", EMAStrategy(short_window=10, long_window=26)),
                ("组合策略", CombinedStrategy(ma_short=10, ma_long=30, rsi_window=21)),
            ]
            print(f"\n[使用指数策略参数 - 更长周期、更宽阈值]")
        else:
            # 个股参数：默认参数，适合捕捉短期波动
            strategies = [
                ("均线策略(SMA)", MovingAverageStrategy(short_window=5, long_window=20)),
                ("RSI策略", RSIStrategy(window=14, oversold=30, overbought=70)),
                ("MACD策略", MACDStrategy(fast=12, slow=26, signal=9)),
                ("布林带策略", BollingerBandsStrategy(window=20, num_std=2)),
                ("KDJ策略", KDJStrategy(k_window=14, d_window=3, oversold=20, overbought=80)),
                ("EMA策略", EMAStrategy(short_window=12, long_window=26)),
                ("组合策略", CombinedStrategy(ma_short=5, ma_long=20, rsi_window=14)),
            ]
            print(f"\n[使用个股策略参数 - 默认参数]")

        # 运行所有策略
        results = []
        print(f"\n{'策略名称':<15} {'收益率':>10} {'夏普比率':>10} {'最大回撤':>10} {'交易次数':>8}")
        print("-" * 70)

        for strategy_name, strategy in strategies:
            try:
                result = run_strategy(strategy_name, strategy, data, symbol)
                results.append(result)
                print(f"{result['name']:<15} {result['return']:>9.2f}% {result['sharpe']:>10.2f} "
                      f"{result['drawdown']:>9.2f}% {result['trades']:>8}")
            except Exception as e:
                print(f"{strategy_name:<15} 运行失败: {e}")

        # 找出最佳策略和最差策略
        if results:
            best_return = max(results, key=lambda x: x['return'])
            best_sharpe = max(results, key=lambda x: x['sharpe'])
            worst_return = min(results, key=lambda x: x['return'])
            worst_sharpe = min(results, key=lambda x: x['sharpe'])

            print(f"\n最佳收益策略: {best_return['name']} ({best_return['return']:.2f}%)")
            print(f"最差收益策略: {worst_return['name']} ({worst_return['return']:.2f}%)")
            print(f"最佳夏普策略: {best_sharpe['name']} ({best_sharpe['sharpe']:.2f})")
            print(f"最差夏普策略: {worst_sharpe['name']} ({worst_sharpe['sharpe']:.2f})")

    print(f"\n{'=' * 70}")
    print("回测完成")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Yahoo Finance 回测工具')
    parser.add_argument(
        '--years',
        type=int,
        default=3,
        help='回测年数，默认3年 (例如: --years 5)'
    )
    args = parser.parse_args()

    run_yahoo_backtest(years=args.years)
