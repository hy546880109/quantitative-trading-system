"""
Market data structures for the trading system.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class BarData:
    """
    K线数据结构
    """
    symbol: str
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    turnover: Optional[float] = None
    open_interest: Optional[int] = None


@dataclass
class TickData:
    """
    Tick数据结构
    """
    symbol: str
    datetime: str
    price: float
    volume: int
    bid_price_1: Optional[float] = None
    bid_volume_1: Optional[int] = None
    ask_price_1: Optional[float] = None
    ask_volume_1: Optional[int] = None


@dataclass
class OrderBookData:
    """
    订单簿数据
    """
    symbol: str
    datetime: str
    bids: list
    asks: list
    last_price: float


class MarketData:
    """
    市场数据处理类
    """
    def __init__(self):
        self.bars = []
        self.ticks = []
        self.order_books = []

    def add_bar(self, bar: BarData):
        """添加K线数据"""
        self.bars.append(bar)

    def add_tick(self, tick: TickData):
        """添加Tick数据"""
        self.ticks.append(tick)

    def get_bars(self, symbol: str, start_date: str, end_date: str):
        """获取指定时间段的K线数据"""
        return [bar for bar in self.bars
                if bar.symbol == symbol
                and start_date <= bar.datetime <= end_date]

    def get_latest_bar(self, symbol: str):
        """获取最新的K线数据"""
        symbol_bars = [bar for bar in self.bars if bar.symbol == symbol]
        if symbol_bars:
            return symbol_bars[-1]
        return None