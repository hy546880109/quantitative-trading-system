"""
技术指标策略实现
"""
import pandas as pd
import numpy as np
from typing import Tuple


class TechnicalIndicators:
    """
    技术指标计算类
    """

    def __init__(self, data: pd.DataFrame):
        """
        初始化技术指标计算器
        :param data: 包含 OHLCV 数据的 DataFrame
        """
        self.data = data.copy()

    def sma(self, window: int = 10) -> pd.Series:
        """
        简单移动平均线 (SMA)
        :param window: 移动平均窗口大小
        :return: SMA 值序列
        """
        return self.data['close'].rolling(window=window).mean()

    def ema(self, window: int = 10) -> pd.Series:
        """
        指数移动平均线 (EMA)
        :param window: 指数平均窗口大小
        :return: EMA 值序列
        """
        return self.data['close'].ewm(span=window).mean()

    def bbands(self, window: int = 20, num_std: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        布林带 (Bollinger Bands)
        :param window: 移动平均窗口大小
        :param num_std: 标准差倍数
        :return: (上轨, 中轨, 下轨) 三元组
        """
        ma = self.data['close'].rolling(window=window).mean()
        std = self.data['close'].rolling(window=window).std()
        upper_band = ma + (std * num_std)
        lower_band = ma - (std * num_std)
        return upper_band, ma, lower_band

    def rsi(self, window: int = 14) -> pd.Series:
        """
        相对强弱指数 (RSI)
        :param window: RSI 计算窗口
        :return: RSI 值序列
        """
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD 指标
        :param fast: 快速EMA周期
        :param slow: 慢速EMA周期
        :param signal: 信号线EMA周期
        :return: (MACD线, 信号线, 柱状图) 三元组
        """
        exp1 = self.data['close'].ewm(span=fast).mean()
        exp2 = self.data['close'].ewm(span=slow).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def atr(self, window: int = 14) -> pd.Series:
        """
        平均真实波幅 (ATR)
        :param window: ATR 计算窗口
        :return: ATR 值序列
        """
        high_low = self.data['high'] - self.data['low']
        high_close = np.abs(self.data['high'] - self.data['close'].shift())
        low_close = np.abs(self.data['low'] - self.data['close'].shift())
        tr = np.max([high_low, high_close, low_close], axis=0)
        atr = pd.Series(tr).rolling(window=window).mean()
        return atr

    def stochastic(self, k_window: int = 14, d_window: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        随机指标 (Stochastic Oscillator)
        :param k_window: %K 窗口大小
        :param d_window: %D 窗口大小
        :return: (%K, %D) 二元组
        """
        lowest_low = self.data['low'].rolling(window=k_window).min()
        highest_high = self.data['high'].rolling(window=k_window).max()
        k_percent = 100 * ((self.data['close'] - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        return k_percent, d_percent


class MovingAverageStrategy:
    """
    移动平均线策略
    """

    def __init__(self, short_window: int = 20, long_window: int = 50):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        :param data: 包含价格数据的DataFrame
        :return: 交易信号序列 (1=买入, -1=卖出, 0=持有)
        """
        ti = TechnicalIndicators(data)
        short_ma = ti.sma(window=self.short_window)
        long_ma = ti.sma(window=self.long_window)

        signals = pd.Series(0, index=data.index)
        # 当短期均线上穿长期均线时买入
        signals[short_ma > long_ma] = 1
        # 当短期均线下穿长期均线时卖出
        signals[short_ma < long_ma] = -1

        return signals


class RSIStrategy:
    """
    RSI策略
    """

    def __init__(self, window: int = 14, oversold: int = 30, overbought: int = 70):
        self.window = window
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        :param data: 包含价格数据的DataFrame
        :return: 交易信号序列 (1=买入, -1=卖出, 0=持有)
        """
        ti = TechnicalIndicators(data)
        rsi_values = ti.rsi(window=self.window)

        signals = pd.Series(0, index=data.index)
        # 当RSI低于超卖线时买入
        signals[rsi_values < self.oversold] = 1
        # 当RSI高于超买线时卖出
        signals[rsi_values > self.overbought] = -1

        return signals


class MACDStrategy:
    """
    MACD策略
    MACD线上穿信号线买入，下穿卖出
    """

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        :param data: 包含价格数据的DataFrame
        :return: 交易信号序列 (1=买入, -1=卖出, 0=持有)
        """
        ti = TechnicalIndicators(data)
        macd_line, signal_line, histogram = ti.macd(
            fast=self.fast, slow=self.slow, signal=self.signal
        )

        signals = pd.Series(0, index=data.index)
        # MACD线上穿信号线买入
        signals[macd_line > signal_line] = 1
        # MACD线下穿信号线卖出
        signals[macd_line < signal_line] = -1

        return signals


class BollingerBandsStrategy:
    """
    布林带策略
    价格触及下轨买入，触及上轨卖出
    """

    def __init__(self, window: int = 20, num_std: int = 2):
        self.window = window
        self.num_std = num_std

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        :param data: 包含价格数据的DataFrame
        :return: 交易信号序列 (1=买入, -1=卖出, 0=持有)
        """
        ti = TechnicalIndicators(data)
        upper, middle, lower = ti.bbands(window=self.window, num_std=self.num_std)

        signals = pd.Series(0, index=data.index)
        close = data['close']

        # 价格触及下轨买入
        signals[close < lower] = 1
        # 价格触及上轨卖出
        signals[close > upper] = -1

        return signals


class KDJStrategy:
    """
    KDJ随机指标策略
    K线上穿D线且处于超卖区买入，下穿且处于超买区卖出
    """

    def __init__(self, k_window: int = 14, d_window: int = 3,
                 oversold: int = 20, overbought: int = 80):
        self.k_window = k_window
        self.d_window = d_window
        self.oversold = oversold
        self.overbought = overbought

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        :param data: 包含价格数据的DataFrame
        :return: 交易信号序列 (1=买入, -1=卖出, 0=持有)
        """
        ti = TechnicalIndicators(data)
        k_percent, d_percent = ti.stochastic(
            k_window=self.k_window, d_window=self.d_window
        )

        signals = pd.Series(0, index=data.index)

        # K线上穿D线且处于超卖区买入
        buy_condition = (k_percent > d_percent) & (k_percent.shift(1) <= d_percent.shift(1)) & (k_percent < self.oversold)
        signals[buy_condition] = 1

        # K线下穿D线且处于超买区卖出
        sell_condition = (k_percent < d_percent) & (k_percent.shift(1) >= d_percent.shift(1)) & (k_percent > self.overbought)
        signals[sell_condition] = -1

        return signals


class EMAStrategy:
    """
    指数移动平均线策略（EMA金叉死叉）
    """

    def __init__(self, short_window: int = 12, long_window: int = 26):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        :param data: 包含价格数据的DataFrame
        :return: 交易信号序列 (1=买入, -1=卖出, 0=持有)
        """
        ti = TechnicalIndicators(data)
        short_ema = ti.ema(window=self.short_window)
        long_ema = ti.ema(window=self.long_window)

        signals = pd.Series(0, index=data.index)
        # 短期EMA上穿长期EMA买入
        signals[short_ema > long_ema] = 1
        # 短期EMA下穿长期EMA卖出
        signals[short_ema < long_ema] = -1

        return signals


class CombinedStrategy:
    """
    组合策略（多指标共振）
    同时满足多个条件才交易
    """

    def __init__(self, ma_short: int = 5, ma_long: int = 20,
                 rsi_window: int = 14, rsi_threshold: int = 50):
        self.ma_short = ma_short
        self.ma_long = ma_long
        self.rsi_window = rsi_window
        self.rsi_threshold = rsi_threshold

    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        :param data: 包含价格数据的DataFrame
        :return: 交易信号序列 (1=买入, -1=卖出, 0=持有)
        """
        ti = TechnicalIndicators(data)

        # 计算指标
        short_ma = ti.sma(window=self.ma_short)
        long_ma = ti.sma(window=self.ma_long)
        rsi = ti.rsi(window=self.rsi_window)

        signals = pd.Series(0, index=data.index)

        # 均线金叉 + RSI确认买入
        buy_condition = (short_ma > long_ma) & (rsi > self.rsi_threshold)
        signals[buy_condition] = 1

        # 均线死叉 + RSI确认卖出
        sell_condition = (short_ma < long_ma) & (rsi < self.rsi_threshold)
        signals[sell_condition] = -1

        return signals