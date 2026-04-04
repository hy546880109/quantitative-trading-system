"""
量化交易系统GUI界面
使用Streamlit实现的Web应用程序
运行: streamlit run gui.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 导入系统模块
import sys
sys.path.insert(0, '.')
from src.data.market_data import BarData, MarketData
from src.data.data_feed import DataFeed
from src.strategies.technical_indicators import (
    TechnicalIndicators, MovingAverageStrategy, RSIStrategy,
    MACDStrategy, BollingerBandsStrategy, KDJStrategy, EMAStrategy
)
from src.core.backtest_engine import BacktestEngine

# 页面配置
st.set_page_config(
    page_title="量化交易系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 移动端优化
st.markdown("""
<style>
    /* 全局样式 */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* 指标卡片优化 */
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
    }

    /* 数据表格优化 */
    .stDataFrame {
        overflow-x: auto;
    }

    /* 正负数颜色 */
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }

    /* 信息框 */
    .info-box {
        background-color: #e7f3ff;
        border-left: 5px solid #2196F3;
        padding: 10px;
        margin: 10px 0;
    }

    /* 移动端响应式适配 */
    @media only screen and (max-width: 768px) {
        /* 调整标题大小 */
        .main-header {
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }

        /* 优化侧边栏 */
        section[data-testid="stSidebar"] {
            width: 100% !important;
        }

        /* 优化指标卡片 */
        .metric-value {
            font-size: 1.2rem;
        }

        /* 优化数据表格 */
        .stDataFrame table {
            font-size: 0.85rem;
        }

        /* 优化按钮 */
        .stButton button {
            width: 100%;
            padding: 8px;
        }

        /* 优化输入框 */
        .stSelectbox, .stSlider, .stNumberInput, .stTextInput {
            font-size: 0.9rem;
        }

        /* 优化图表高度 */
        .js-plotly-plot {
            height: 400px !important;
        }

        /* 优化expander */
        .streamlit-expanderContent {
            padding: 10px;
        }
    }

    /* 超小屏幕优化 (< 480px) */
    @media only screen and (max-width: 480px) {
        .main-header {
            font-size: 1.5rem;
        }

        .metric-value {
            font-size: 1rem;
        }

        /* 隐藏部分次要信息 */
        .stMarkdown h3 {
            font-size: 1rem;
        }

        /* 增加触摸友好性 */
        button, select, input {
            min-height: 44px;
        }
    }

    /* 横屏模式优化 */
    @media screen and (orientation: landscape) and (max-width: 768px) {
        section[data-testid="stSidebar"] {
            width: 30% !important;
        }

        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }

    /* 高分辨率设备 */
    @media only screen and (min-width: 1920px) {
        .main-header {
            font-size: 3rem;
        }

        .metric-value {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def generate_mock_data(start_date, end_date):
    """生成模拟数据"""
    start = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')

    dates = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            dates.append(current)
        current += timedelta(days=1)

    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 2)

    df = pd.DataFrame({
        'open': prices + np.random.randn(len(dates)) * 0.5,
        'high': prices + np.abs(np.random.randn(len(dates))) * 2,
        'low': prices - np.abs(np.random.randn(len(dates))) * 2,
        'close': prices,
        'volume': np.random.randint(1000000, 5000000, len(dates))
    }, index=dates)

    return df

def bars_to_dataframe(bars):
    """转换BarData到DataFrame"""
    if not bars:
        raise ValueError("没有获取到数据")

    data = {
        'open': [bar.open for bar in bars],
        'high': [bar.high for bar in bars],
        'low': [bar.low for bar in bars],
        'close': [bar.close for bar in bars],
        'volume': [bar.volume for bar in bars]
    }
    dates = [bar.datetime for bar in bars]
    return pd.DataFrame(data, index=pd.to_datetime(dates))

def get_strategy(strategy_name, params):
    """获取策略对象"""
    if strategy_name == "移动平均线策略 (MA)":
        return MovingAverageStrategy(
            short_window=params['short_window'],
            long_window=params['long_window']
        )
    elif strategy_name == "RSI策略":
        return RSIStrategy(
            window=params['rsi_window'],
            oversold=params['oversold'],
            overbought=params['overbought']
        )
    elif strategy_name == "MACD策略":
        return MACDStrategy(
            fast=params['fast'],
            slow=params['slow'],
            signal=params['signal']
        )
    elif strategy_name == "布林带策略":
        return BollingerBandsStrategy(
            window=params['bb_window'],
            num_std=params['num_std']
        )
    elif strategy_name == "KDJ策略":
        return KDJStrategy(
            k_window=params['k_window'],
            d_window=params['d_window']
        )
    elif strategy_name == "EMA策略":
        return EMAStrategy(
            short_window=params['ema_short'],
            long_window=params['ema_long']
        )
    return MovingAverageStrategy()

def format_price(price: float | None, symbol: str) -> str:
    """
    根据股票代码格式化价格显示

    Args:
        price: 价格数值（支持None、NaN等异常值）
        symbol: 股票代码

    Returns:
        格式化的价格字符串（美股指数用$，其他用¥）
    """
    # Handle invalid prices
    if price is None or not isinstance(price, (int, float)):
        return "--"
    if math.isnan(price) or math.isinf(price):
        return "--"

    # Determine currency based on symbol
    # US indices (^DJI, ^GSPC, ^IXIC) and US stocks (no dots, all caps) use $
    is_us_market = symbol.startswith('^') or (symbol.isupper() and '.' not in symbol)

    currency = "$" if is_us_market else "¥"
    return f"{currency}{price:,.2f}"

def plot_candlestick(df, trades=None):
    """绘制K线图"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                       vertical_spacing=0.03,
                       row_heights=[0.7, 0.3])

    # K线图
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='K线'
    ), row=1, col=1)

    # 成交量
    colors = ['green' if df['close'].iloc[i] >= df['open'].iloc[i] else 'red'
              for i in range(len(df))]
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['volume'],
        marker_color=colors,
        name='成交量'
    ), row=2, col=1)

    # 标记买卖点
    if trades:
        for trade in trades:
            trade_date = pd.to_datetime(trade['date'])
            if trade['action'] == 'BUY':
                fig.add_trace(go.Scatter(
                    x=[trade_date],
                    y=[trade['price']],
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=15, color='red'),
                    name='买入'
                ), row=1, col=1)
            else:
                fig.add_trace(go.Scatter(
                    x=[trade_date],
                    y=[trade['price']],
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=15, color='green'),
                    name='卖出'
                ), row=1, col=1)

    fig.update_layout(
        title='股票价格走势',
        yaxis_title='价格',
        xaxis_title='日期',
        height=600
    )

    return fig

def plot_equity_curve(result):
    """绘制资金曲线"""
    equity_curve = result['equity_curve']
    dates = [pd.to_datetime(point['date']) for point in equity_curve]
    portfolio_values = [point['portfolio_value'] for point in equity_curve]
    cash_values = [point['cash'] for point in equity_curve]
    holdings = [v - c for v, c in zip(portfolio_values, cash_values)]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                       vertical_spacing=0.08,
                       subplot_titles=('资金曲线', '持仓分布'))

    # 资金曲线
    fig.add_trace(go.Scatter(
        x=dates, y=portfolio_values,
        mode='lines',
        name='总资产',
        line=dict(color='blue', width=2)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=dates, y=[result['initial_capital']] * len(dates),
        mode='lines',
        name='初始资金',
        line=dict(color='gray', dash='dash')
    ), row=1, col=1)

    # 持仓
    fig.add_trace(go.Scatter(
        x=dates, y=holdings,
        mode='lines',
        name='持仓市值',
        fill='tozeroy',
        line=dict(color='orange')
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=dates, y=cash_values,
        mode='lines',
        name='现金',
        line=dict(color='green')
    ), row=2, col=1)

    fig.update_layout(
        title=f'回测结果 - 总收益率: {result["total_return_pct"]:.2f}%',
        height=700
    )

    return fig

def main():
    """主函数"""
    # 标题
    st.markdown('<div class="main-header">📈 量化交易系统 v1.0</div>', unsafe_allow_html=True)

    # 侧边栏 - 配置
    with st.sidebar:
        st.header("⚙️ 系统配置")

        # 股票代码选择
        st.subheader("📈 股票代码")

        # 热门股票列表
        popular_stocks = {
            "🔥 热门A股": {
                "000001.SZ": "平安银行",
                "000858.SZ": "五粮液",
                "002415.SZ": "海康威视",
                "600519.SH": "贵州茅台",
                "600036.SH": "招商银行",
                "601318.SH": "中国平安",
                "000333.SZ": "美的集团",
                "002594.SZ": "比亚迪",
                "600276.SH": "恒瑞医药",
                "601012.SH": "隆基绿能"
            },
            "📊 主要指数": {
                "000001.SH": "上证指数",
                "399001.SZ": "深证成指",
                "399006.SZ": "创业板指",
                "000300.SH": "沪深300",
                "000016.SH": "上证50",
                "000905.SH": "中证500"
            },
            "🇺🇸 美股指数": {
                "^GSPC": "标普500",
                "^IXIC": "纳斯达克指数",
                "^DJI": "道琼斯指数"
            },
            "🌐 美股热门": {
                "AAPL": "苹果公司",
                "MSFT": "微软",
                "GOOGL": "谷歌",
                "AMZN": "亚马逊",
                "TSLA": "特斯拉",
                "NVDA": "英伟达",
                "META": "Meta",
                "BABA": "阿里巴巴"
            },
            "🧪 测试用": {
                "TEST": "模拟测试"
            }
        }

        # 选择股票类别
        stock_category = st.selectbox("选择股票类别", list(popular_stocks.keys()))

        # 显示该类别下的股票
        stocks_in_category = popular_stocks[stock_category]
        stock_display = [f"{code} - {name}" for code, name in stocks_in_category.items()]
        selected_display = st.selectbox("选择股票", stock_display)

        # 提取股票代码
        symbol = selected_display.split(" - ")[0]

        # 显示当前选择的代码
        st.info(f"**当前股票代码**: `{symbol}`")

        # 手动输入选项
        use_custom = st.checkbox("手动输入股票代码")
        if use_custom:
            symbol = st.text_input("输入股票代码", value=symbol, help="格式: A股代码.SZ/SH, 美股直接输入代码")

            # 显示格式说明
            with st.expander("📖 股票代码格式说明"):
                st.markdown("""
                **A股代码格式** (TuShare):
                - 深圳证券交易所: `000001.SZ`, `002594.SZ`, `399006.SZ`
                - 上海证券交易所: `600519.SH`, `601318.SH`, `000001.SH`

                **美股代码** (Yahoo Finance):
                - 直接输入: `AAPL`, `MSFT`, `TSLA`, `BABA`

                **港股代码** (Yahoo Finance):
                - 格式: `0700.HK`, `3690.HK`
                """)

        # 数据源配置
        st.subheader("📊 数据源")

        # 检查是否为美股指数
        if stock_category == "🇺🇸 美股指数":
            # 美股指数强制使用Yahoo Finance
            st.info("ℹ️ 美股指数使用 Yahoo Finance 数据源")
            data_source = st.selectbox(
                "选择数据源",
                ["Yahoo Finance"],
                disabled=True,
                help="美股指数仅支持Yahoo Finance数据源"
            )
        else:
            # 其他分类正常选择数据源
            data_source = st.selectbox(
                "选择数据源",
                ["模拟数据", "TuShare", "Yahoo Finance"]
            )

        if data_source == "TuShare":
            token = st.text_input("TuShare Token", type="password")
        else:
            token = None

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "开始日期",
                value=datetime.now() - timedelta(days=365)
            )
        with col2:
            end_date = st.date_input(
                "结束日期",
                value=datetime.now()
            )

        # 策略配置
        st.subheader("🎯 交易策略")
        strategy_name = st.selectbox(
            "选择策略",
            ["移动平均线策略 (MA)", "RSI策略", "MACD策略", "布林带策略", "KDJ策略", "EMA策略"]
        )

        # 策略参数
        params = {}
        if strategy_name == "移动平均线策略 (MA)":
            params['short_window'] = st.slider("短期窗口", 5, 50, 10)
            params['long_window'] = st.slider("长期窗口", 20, 200, 30)

        elif strategy_name == "RSI策略":
            params['rsi_window'] = st.slider("RSI周期", 2, 50, 14)
            params['oversold'] = st.slider("超卖阈值", 10, 40, 30)
            params['overbought'] = st.slider("超买阈值", 60, 90, 70)

        elif strategy_name == "MACD策略":
            params['fast'] = st.slider("快速EMA", 5, 30, 12)
            params['slow'] = st.slider("慢速EMA", 20, 50, 26)
            params['signal'] = st.slider("信号线", 5, 20, 9)

        elif strategy_name == "布林带策略":
            params['bb_window'] = st.slider("窗口大小", 10, 50, 20)
            params['num_std'] = st.slider("标准差倍数", 1, 4, 2)

        elif strategy_name == "KDJ策略":
            params['k_window'] = st.slider("K线周期", 5, 30, 9)
            params['d_window'] = st.slider("D线周期", 1, 10, 3)

        elif strategy_name == "EMA策略":
            params['ema_short'] = st.slider("短期EMA", 5, 30, 12)
            params['ema_long'] = st.slider("长期EMA", 20, 50, 26)

        # 初始资金
        st.subheader("💰 资金配置")
        initial_capital = st.number_input(
            "初始资金 (¥)",
            min_value=1000,
            max_value=100000000,
            value=100000,
            step=10000
        )

        # 加载数据按钮
        st.markdown("---")
        load_data_btn = st.button("📥 加载数据", use_container_width=True)
        run_backtest_btn = st.button("🚀 运行回测", use_container_width=True, type="primary")

    # 主界面
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'backtest_result' not in st.session_state:
        st.session_state.backtest_result = None

    # 加载数据
    if load_data_btn:
        with st.spinner("正在加载数据..."):
            try:
                if data_source == "模拟数据":
                    st.session_state.data = generate_mock_data(
                        start_date.strftime('%Y%m%d'),
                        end_date.strftime('%Y%m%d')
                    )
                elif data_source == "TuShare":
                    if not token:
                        st.error("请提供TuShare Token")
                    else:
                        feed = DataFeed("tushare", token)
                        bars = feed.fetch_daily_data(
                            symbol,
                            start_date.strftime('%Y%m%d'),
                            end_date.strftime('%Y%m%d')
                        )
                        st.session_state.data = bars_to_dataframe(bars)
                elif data_source == "Yahoo Finance":
                    feed = DataFeed("yahoo")
                    bars = feed.fetch_daily_data(
                        symbol,
                        start_date.strftime('%Y%m%d'),
                        end_date.strftime('%Y%m%d')
                    )
                    st.session_state.data = bars_to_dataframe(bars)

                if st.session_state.data is not None:
                    st.success(f"✅ 数据加载成功！共 {len(st.session_state.data)} 条记录")

            except Exception as e:
                st.error(f"❌ 数据加载失败: {str(e)}")

    # 显示数据预览
    if st.session_state.data is not None:
        st.subheader("📋 数据预览")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("数据条数", len(st.session_state.data))
        with col2:
            st.metric("起始日期", st.session_state.data.index[0].strftime('%Y-%m-%d'))
        with col3:
            st.metric("结束日期", st.session_state.data.index[-1].strftime('%Y-%m-%d'))
        with col4:
            latest_close = st.session_state.data['close'].iloc[-1]
            st.metric("最新收盘价", format_price(latest_close, symbol))

        # 数据表格
        st.dataframe(
            st.session_state.data.head(20).style.format({
                'open': '¥{:.2f}',
                'high': '¥{:.2f}',
                'low': '¥{:.2f}',
                'close': '¥{:.2f}',
                'volume': '{:,.0f}'
            }),
            use_container_width=True
        )

        # K线图
        st.plotly_chart(plot_candlestick(st.session_state.data), use_container_width=True)

    # 运行回测
    if run_backtest_btn:
        if st.session_state.data is None:
            st.error("⚠️ 请先加载数据")
        else:
            with st.spinner("正在执行回测..."):
                try:
                    strategy = get_strategy(strategy_name, params)
                    engine = BacktestEngine(initial_capital=initial_capital)
                    result = engine.run_backtest(strategy, st.session_state.data, symbol)
                    st.session_state.backtest_result = result
                    st.success("✅ 回测执行成功！")
                except Exception as e:
                    st.error(f"❌ 回测执行失败: {str(e)}")

    # 显示回测结果
    if st.session_state.backtest_result:
        result = st.session_state.backtest_result

        st.markdown("---")
        st.subheader("📊 回测结果")

        # 指标卡片
        cols = st.columns(6)
        metrics = [
            ("初始资金", f"¥{result['initial_capital']:,.2f}"),
            ("最终价值", f"¥{result['final_value']:,.2f}"),
            ("总收益率", f"{result['total_return_pct']:.2f}%"),
            ("夏普比率", f"{result['sharpe_ratio']:.2f}"),
            ("最大回撤", f"{result['max_drawdown']:.2f}%"),
            ("交易次数", str(result['total_trades']))
        ]

        for col, (name, value) in zip(cols, metrics):
            with col:
                if name == "总收益率":
                    delta_color = "normal" if result['total_return_pct'] >= 0 else "inverse"
                    st.metric(name, value, delta=f"{result['total_return_pct']:.2f}%", delta_color=delta_color)
                else:
                    st.metric(name, value)

        # 资金曲线
        st.plotly_chart(plot_equity_curve(result), use_container_width=True)

        # 交易记录
        st.subheader("📝 交易记录")
        if result['trades']:
            trades_df = pd.DataFrame(result['trades'])
            trades_df['date'] = pd.to_datetime(trades_df['date']).dt.strftime('%Y-%m-%d')
            trades_df['price'] = trades_df['price'].apply(lambda x: f"¥{x:.2f}")
            trades_df['total'] = trades_df['total'].apply(lambda x: f"¥{x:,.2f}")
            trades_df.columns = ['日期', '股票代码', '操作', '数量', '价格', '总金额']
            st.dataframe(trades_df, use_container_width=True)
        else:
            st.info("没有交易记录")

    # 使用说明 - 默认展开
    with st.expander("📖 使用说明", expanded=True):
        st.markdown("""
        ### 使用步骤
        1. **配置数据源**：选择数据源类型（模拟数据/TuShare/Yahoo Finance），输入股票代码
        2. **设置策略参数**：选择交易策略并调整参数
        3. **设置资金**：输入初始资金金额
        4. **加载数据**：点击"加载数据"按钮
        5. **运行回测**：点击"运行回测"按钮查看结果

        ### 支持的数据源
        - **模拟数据**：生成随机模拟数据，无需配置
        - **TuShare**：需要TuShare Token，支持A股数据
        - **Yahoo Finance**：无需Token，支持全球股票

        ### 支持的交易策略
        - 移动平均线策略 (MA)
        - RSI策略
        - MACD策略
        - 布林带策略
        - KDJ策略
        - EMA策略
        """)

if __name__ == "__main__":
    main()
