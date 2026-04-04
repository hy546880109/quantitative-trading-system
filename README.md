# 量化交易系统

基于 TDD 和子代理驱动开发模式构建的量化交易系统。

## 项目结构

```
quantitative-trading-system/
├── src/
│   ├── __init__.py
│   ├── data/               # 数据层
│   │   ├── market_data.py  # K线、Tick、订单簿数据结构
│   │   └── data_feed.py    # 数据接口（TuShare/Yahoo实现）
│   ├── strategies/         # 策略层
│   │   └── technical_indicators.py  # 技术指标计算
│   ├── core/               # 核心引擎
│   │   └── backtest_engine.py       # 回测引擎
│   └── utils/              # 工具函数
├── tests/                  # 测试套件
├── main.py                 # 主程序（演示系统）
├── gui.py                  # 🆕 Streamlit GUI界面
├── real_stock_backtest.py  # 真实股票回测（TuShare）
├── yahoo_backtest.py       # Yahoo Finance回测（无需token）
├── requirements.txt        # 依赖列表
├── README.md
├── DATA_SOURCE_GUIDE.md    # 数据源配置指南
├── 量化交易系统开发实战指南.md
└── Superpowers插件深度解析.md
```

## 安装依赖

```bash
cd quantitative-trading-system
pip install -r requirements.txt
```

## 快速运行

### 🖥️ 运行GUI界面（推荐）

使用 Streamlit 实现的交互式 Web 界面，无需编程即可使用：

```bash
cd quantitative-trading-system

# 安装依赖
pip install streamlit plotly

# 启动GUI
streamlit run gui.py
```

浏览器将自动打开 `http://localhost:8501`

**GUI功能特性：**
- 📊 可视化股票选择（热门A股、指数、美股）
- 🎯 6种内置策略（MA、RSI、MACD、布林带、KDJ、EMA）
- 📈 实时K线图、资金曲线、持仓分布
- 📋 交易记录表格
- 💰 回测指标展示（收益率、夏普比率、最大回撤）

---

### 1. 运行演示系统

```bash
cd quantitative-trading-system
python main.py
```

### 2. 使用真实股票数据回测

#### 步骤1: 获取TuShare Token

1. 访问 https://tushare.pro/register 注册账号
2. 在个人中心获取token
3. 设置环境变量:

```bash
export TUSHARE_TOKEN=your_token_here
```

或在Windows PowerShell:
```powershell
$env:TUSHARE_TOKEN="your_token_here"
```

#### 步骤2: 运行真实数据回测

```bash
cd quantitative-trading-system
python real_stock_backtest.py
```

示例输出：
```
正在连接TuShare数据源...

获取 000001.SZ 股票数据:
  时间范围: 20240327 ~ 20250327
  成功获取 242 条K线数据

数据概览:
  起始日期: 20240327
  结束日期: 20250327
  最高价格: ¥13.50
  最低价格: ¥9.80
  最新收盘: ¥12.35

============================================================
策略1: 均线交叉策略
============================================================
均线策略回测结果:
  初始资金: ¥100,000.00
  最终价值: ¥115,230.50
  总收益率: 15.23%
  夏普比率: 1.25
  最大回撤: 8.50%
  总交易次数: 12

============================================================
策略2: RSI策略
============================================================
RSI策略回测结果:
  初始资金: ¥100,000.00
  最终价值: ¥108,450.20
  总收益率: 8.45%
  夏普比率: 0.85
  最大回撤: 6.20%
  总交易次数: 8

============================================================
策略对比
============================================================
表现更好: 均线策略
  均线策略收益率: 15.23%
  RSI策略收益率: 8.45%
  收益差值: 6.78%
```

### 3. 使用Yahoo Finance数据（无需token）

如果不想注册TuShare，可以使用Yahoo Finance数据源：

```bash
# 安装yfinance
pip install yfinance

# 运行Yahoo数据回测
cd quantitative-trading-system
python yahoo_backtest.py
```

支持的股票代码格式：
- A股: `000001.SZ` (深圳), `600519.SH` (上海)
- 港股: `0700.HK`
- 美股: `AAPL`, `MSFT`, `TSLA`

### 4. 运行测试

```bash
cd quantitative-trading-system
python -m pytest tests/ -v
```

## 快速使用

### 1. 数据结构

```python
from src.data.market_data import BarData, TickData, MarketData

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

# 市场数据管理
market = MarketData()
market.add_bar(bar)
latest = market.get_latest_bar("000001.SZ")
```

### 2. 技术指标计算

```python
import pandas as pd
from src.strategies.technical_indicators import TechnicalIndicators

# 模拟价格数据
data = pd.DataFrame({
    'open': [10, 11, 12, 11, 13],
    'high': [11, 12, 13, 12, 14],
    'low': [9, 10, 11, 10, 12],
    'close': [10.5, 11.2, 12.1, 11.5, 13.2],
    'volume': [1000, 1100, 1200, 1150, 1300]
})

ti = TechnicalIndicators(data)

# 简单移动平均
sma = ti.sma(window=3)

# 指数移动平均
ema = ti.ema(window=3)

# MACD
macd, signal, histogram = ti.macd()

# RSI
rsi = ti.rsi(window=3)

# 布林带
upper, middle, lower = ti.bbands(window=3)

# ATR
atr = ti.atr(window=3)
```

### 3. 交易策略

```python
import pandas as pd
from src.strategies.technical_indicators import (
    TechnicalIndicators, MovingAverageStrategy, RSIStrategy
)

data = pd.DataFrame({
    'open': [10, 11, 12, 11, 13, 12, 14, 15, 14, 16],
    'high': [11, 12, 13, 12, 14, 13, 15, 16, 15, 17],
    'low': [9, 10, 11, 10, 12, 11, 13, 14, 13, 15],
    'close': [10.5, 11.2, 12.1, 11.5, 13.2, 12.8, 14.5, 15.3, 14.8, 16.2],
    'volume': [1000, 1100, 1200, 1150, 1300, 1250, 1400, 1500, 1450, 1600]
})

# 均线策略（金叉/死叉）
ma_strategy = MovingAverageStrategy(short_window=3, long_window=5)
ma_signals = ma_strategy.generate_signals(data)

# RSI策略
rsi_strategy = RSIStrategy(window=3, oversold=30, overbought=70)
rsi_signals = rsi_strategy.generate_signals(data)

print("均线信号:", ma_signals.tolist())
print("RSI信号:", rsi_signals.tolist())
```

### 4. 运行回测

```python
import pandas as pd
from src.core.backtest_engine import BacktestEngine
from src.strategies.technical_indicators import MovingAverageStrategy

# 准备历史数据
data = pd.DataFrame({
    'open': [10, 11, 12, 11, 13, 12, 14, 15, 14, 16,
             15, 17, 16, 18, 17, 19, 18, 20, 19, 21],
    'high': [11, 12, 13, 12, 14, 13, 15, 16, 15, 17,
             16, 18, 17, 19, 18, 20, 19, 21, 20, 22],
    'low': [9, 10, 11, 10, 12, 11, 13, 14, 13, 15,
            14, 16, 15, 17, 16, 18, 17, 19, 18, 20],
    'close': [10.5, 11.2, 12.1, 11.5, 13.2, 12.8, 14.5, 15.3, 14.8, 16.2,
              15.5, 17.2, 16.3, 18.1, 17.5, 19.2, 18.6, 20.5, 19.8, 21.5],
    'volume': [1000, 1100, 1200, 1150, 1300, 1250, 1400, 1500, 1450, 1600,
               1550, 1700, 1650, 1800, 1750, 1900, 1850, 2000, 1950, 2100]
})

# 创建策略和回测引擎
strategy = MovingAverageStrategy(short_window=5, long_window=10)
engine = BacktestEngine(initial_capital=100000)

# 运行回测
result = engine.run_backtest(strategy, data, symbol="000001.SZ")

# 打印回测结果
print("=" * 50)
print("回测结果")
print("=" * 50)
print(f"初始资金: ¥{result['initial_capital']:,.2f}")
print(f"最终价值: ¥{result['final_value']:,.2f}")
print(f"总收益率: {result['total_return_pct']:.2f}%")
print(f"夏普比率: {result['sharpe_ratio']:.2f}")
print(f"最大回撤: {result['max_drawdown']:.2f}%")
print(f"总交易次数: {result['total_trades']}")
print(f"买入次数: {result['buy_trades']}")
print(f"卖出次数: {result['sell_trades']}")
```

### 5. 使用TuShare获取真实数据

```python
from src.data.data_feed import DataFeed, DataFeedInterface

# 创建数据源
feed = DataFeed.create("tushare", token="your_tushare_token")

# 获取股票数据
data = feed.fetch_daily_data(
    symbol="000001.SZ",
    start_date="20230101",
    end_date="20240101"
)

print(f"获取到 {len(data)} 条K线数据")
```

## 核心功能

| 模块 | 功能 | 说明 |
|-----|------|------|
| `market_data` | 数据结构 | BarData、K线、Tick、订单簿 |
| `data_feed` | 数据接口 | TuShare数据源适配器 |
| `technical_indicators` | 技术指标 | SMA、EMA、MACD、RSI、布林带、ATR、KDJ |
| `backtest_engine` | 回测引擎 | 夏普比率、最大回撤、交易统计 |

## 开发方式

本项目使用 Superpowers 插件的 TDD 工作流开发：

1. `brainstorming` - 需求分析
2. `writing-plans` - 编写实现计划
3. `subagent-driven-development` - 子代理执行
4. `test-driven-development` - 测试驱动开发

详见 `Superpowers插件深度解析.md`

## 🌐 Streamlit Cloud 部署

本项目支持部署到 Streamlit Cloud，在线使用真实数据源：

1. Fork 本仓库到你的 GitHub
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 点击 "New app"，选择你的仓库
4. 设置 Main file path: `gui.py`
5. 点击 Deploy

部署完成后，你可以在云端使用 TuShare 或 Yahoo Finance 真实数据进行回测。