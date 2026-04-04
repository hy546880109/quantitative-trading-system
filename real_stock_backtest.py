"""
真实股票数据回测示例
需要TuShare账号和token: https://tushare.pro/register
"""
import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.data_feed import DataFeed
from src.strategies.technical_indicators import MovingAverageStrategy, RSIStrategy
from src.core.backtest_engine import BacktestEngine


def bars_to_dataframe(bars):
    """将BarData列表转换为DataFrame"""
    if not bars:
        return pd.DataFrame()

    data = {
        'open': [bar.open for bar in bars],
        'high': [bar.high for bar in bars],
        'low': [bar.low for bar in bars],
        'close': [bar.close for bar in bars],
        'volume': [bar.volume for bar in bars]
    }
    index = [bar.datetime for bar in bars]
    return pd.DataFrame(data, index=index)


def run_backtest_with_real_data():
    """使用真实股票数据运行回测"""

    # 获取TuShare token
    # 方式1: 从环境变量获取
    token = os.environ.get('TUSHARE_TOKEN')

    # 方式2: 直接设置（不推荐用于生产环境）
    # token = "your_token_here"

    if not token:
        print("=" * 60)
        print("错误: 未设置TuShare Token")
        print("=" * 60)
        print("\n请按以下步骤操作:")
        print("1. 访问 https://tushare.pro/register 注册账号")
        print("2. 在个人中心获取token")
        print("3. 设置环境变量:")
        print("   export TUSHARE_TOKEN=your_token_here")
        print("\n或在代码中临时设置（仅测试）:")
        print("   token = 'your_token_here'")
        print("=" * 60)
        return

    # 创建数据源
    print("正在连接TuShare数据源...")
    try:
        feed = DataFeed("tushare", token)
    except Exception as e:
        print(f"连接失败: {e}")
        return

    # 设置回测参数
    symbol = "000001.SZ"  # 平安银行
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 过去一年数据

    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')

    print(f"\n获取 {symbol} 股票数据:")
    print(f"  时间范围: {start_date_str} ~ {end_date_str}")

    # 获取数据
    bars = feed.fetch_daily_data(symbol, start_date_str, end_date_str)

    if not bars:
        print("获取数据失败，请检查token和网络连接")
        return

    print(f"  成功获取 {len(bars)} 条K线数据")

    # 转换为DataFrame
    data = bars_to_dataframe(bars)

    # 显示数据概览
    print(f"\n数据概览:")
    print(f"  起始日期: {data.index[0]}")
    print(f"  结束日期: {data.index[-1]}")
    print(f"  最高价格: ¥{data['high'].max():.2f}")
    print(f"  最低价格: ¥{data['low'].min():.2f}")
    print(f"  最新收盘: ¥{data['close'].iloc[-1]:.2f}")

    # 创建策略
    print("\n" + "=" * 60)
    print("策略1: 均线交叉策略")
    print("=" * 60)

    ma_strategy = MovingAverageStrategy(short_window=5, long_window=20)
    ma_engine = BacktestEngine(initial_capital=100000)
    ma_result = ma_engine.run_backtest(ma_strategy, data, symbol=symbol)

    print(f"\n均线策略回测结果:")
    print(f"  初始资金: ¥{ma_result['initial_capital']:,.2f}")
    print(f"  最终价值: ¥{ma_result['final_value']:,.2f}")
    print(f"  总收益率: {ma_result['total_return_pct']:.2f}%")
    print(f"  夏普比率: {ma_result['sharpe_ratio']:.2f}")
    print(f"  最大回撤: {ma_result['max_drawdown']:.2f}%")
    print(f"  总交易次数: {ma_result['total_trades']}")

    # 策略2: RSI策略
    print("\n" + "=" * 60)
    print("策略2: RSI策略")
    print("=" * 60)

    rsi_strategy = RSIStrategy(window=14, oversold=30, overbought=70)
    rsi_engine = BacktestEngine(initial_capital=100000)
    rsi_result = rsi_engine.run_backtest(rsi_strategy, data, symbol=symbol)

    print(f"\nRSI策略回测结果:")
    print(f"  初始资金: ¥{rsi_result['initial_capital']:,.2f}")
    print(f"  最终价值: ¥{rsi_result['final_value']:,.2f}")
    print(f"  总收益率: {rsi_result['total_return_pct']:.2f}%")
    print(f"  夏普比率: {rsi_result['sharpe_ratio']:.2f}")
    print(f"  最大回撤: {rsi_result['max_drawdown']:.2f}%")
    print(f"  总交易次数: {rsi_result['total_trades']}")

    # 对比分析
    print("\n" + "=" * 60)
    print("策略对比")
    print("=" * 60)

    ma_return = ma_result['total_return_pct']
    rsi_return = rsi_result['total_return_pct']

    better_strategy = "均线策略" if ma_return > rsi_return else "RSI策略"
    print(f"\n表现更好: {better_strategy}")
    print(f"  均线策略收益率: {ma_return:.2f}%")
    print(f"  RSI策略收益率: {rsi_return:.2f}%")
    print(f"  收益差值: {abs(ma_return - rsi_return):.2f}%")

    # 显示最近的交易记录
    if ma_result['trades']:
        print(f"\n均线策略最近5笔交易:")
        for trade in ma_result['trades'][-5:]:
            print(f"  {trade['date'][:10]} | {trade['action']:4} | "
                  f"数量:{trade['quantity']:4} | 价格:¥{trade['price']:.2f}")


if __name__ == "__main__":
    run_backtest_with_real_data()
