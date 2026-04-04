"""
数据源接口模块
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import pandas as pd
import tushare as ts
from src.data.market_data import BarData


class DataFeedInterface(ABC):
    """数据源接口"""

    @abstractmethod
    def fetch_daily_data(self, symbol: str, start_date: str, end_date: str) -> List[BarData]:
        """获取日线数据"""
        pass

    @abstractmethod
    def fetch_minute_data(self, symbol: str, start_date: str, end_date: str) -> List[BarData]:
        """获取分钟线数据"""
        pass

    @abstractmethod
    def fetch_current_data(self, symbol: str) -> Optional[BarData]:
        """获取当前数据"""
        pass


class TuShareDataFeed(DataFeedInterface):
    """TuShare数据源实现"""

    # A股指数代码集合
    INDEX_SYMBOLS = {
        "000001.SH", "399001.SZ", "399006.SZ",
        "000300.SH", "000016.SH", "000905.SH",
        "000010.SH", "000009.SH", "399005.SZ"
    }

    def __init__(self, token: str):
        self.token = token
        ts.set_token(token)
        self.pro = ts.pro_api()

    def _is_index(self, symbol: str) -> bool:
        """判断是否为指数代码"""
        return symbol in self.INDEX_SYMBOLS

    def fetch_daily_data(self, symbol: str, start_date: str, end_date: str) -> List[BarData]:
        """获取日线数据"""
        try:
            # 判断是否为指数
            if self._is_index(symbol):
                # 使用指数接口
                df = self.pro.index_daily(ts_code=symbol, start_date=start_date, end_date=end_date)
            else:
                # 使用个股接口
                df = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)

            if df.empty:
                print(f"未获取到 {symbol} 的数据")
                return []

            bars = []
            for _, row in df.iterrows():
                bar = BarData(
                    symbol=row['ts_code'],
                    datetime=row['trade_date'],
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['vol']) if 'vol' in row else int(row.get('volume', 0))
                )
                bars.append(bar)
            return bars
        except Exception as e:
            print(f"Error fetching daily data for {symbol}: {e}")
            return []

    def fetch_minute_data(self, symbol: str, start_date: str, end_date: str) -> List[BarData]:
        """获取分钟线数据"""
        # TuShare的分钟数据需要专业版权限
        print("Minute data requires TuShare Pro subscription")
        return []

    def fetch_current_data(self, symbol: str) -> Optional[BarData]:
        """获取当前数据"""
        try:
            # 获取实时数据
            df = self.pro.daily(ts_code=symbol, start_date=datetime.now().strftime('%Y%m%d'),
                               end_date=datetime.now().strftime('%Y%m%d'))
            if not df.empty:
                row = df.iloc[0]
                return BarData(
                    symbol=row['ts_code'],
                    datetime=row['trade_date'],
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['vol'])
                )
            return None
        except Exception as e:
            print(f"Error fetching current data: {e}")
            return None


class YahooFinanceDataFeed(DataFeedInterface):
    """Yahoo Finance数据源实现（备选，无需token）"""

    def __init__(self, token: str = None):
        self.token = token
        try:
            import yfinance as yf
            self.yf = yf
        except ImportError:
            print("请先安装yfinance: pip install yfinance")
            raise

    def _convert_symbol(self, symbol: str) -> str:
        """转换股票代码格式"""
        # 中国A股转换
        if symbol.endswith('.SH'):
            return symbol.replace('.SH', '.SS')
        elif symbol.endswith('.SZ'):
            return symbol.replace('.SZ', '.SZ')
        return symbol

    def fetch_daily_data(self, symbol: str, start_date: str, end_date: str) -> List[BarData]:
        """获取日线数据"""
        try:
            # 转换日期格式
            start = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')

            # 转换股票代码
            yahoo_symbol = self._convert_symbol(symbol)

            # 下载数据
            ticker = self.yf.Ticker(yahoo_symbol)
            df = ticker.history(start=start, end=end)

            bars = []
            for date, row in df.iterrows():
                bar = BarData(
                    symbol=symbol,
                    datetime=date.strftime('%Y-%m-%d'),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume'])
                )
                bars.append(bar)
            return bars
        except Exception as e:
            print(f"Error fetching Yahoo Finance data: {e}")
            return []

    def fetch_minute_data(self, symbol: str, start_date: str, end_date: str) -> List[BarData]:
        """获取分钟线数据"""
        print("Minute data not implemented for Yahoo Finance")
        return []

    def fetch_current_data(self, symbol: str) -> Optional[BarData]:
        """获取当前数据"""
        try:
            yahoo_symbol = self._convert_symbol(symbol)
            ticker = self.yf.Ticker(yahoo_symbol)
            info = ticker.info

            if 'regularMarketPrice' in info:
                return BarData(
                    symbol=symbol,
                    datetime=datetime.now().strftime('%Y-%m-%d'),
                    open=info.get('regularMarketOpen', 0),
                    high=info.get('regularMarketDayHigh', 0),
                    low=info.get('regularMarketDayLow', 0),
                    close=info['regularMarketPrice'],
                    volume=info.get('regularMarketVolume', 0)
                )
            return None
        except Exception as e:
            print(f"Error fetching current data: {e}")
            return None


class DataFeed:
    """数据源工厂类"""

    def __init__(self, source: str, token: str = None):
        self.source = source
        self.token = token
        self._data_feed = self._create_data_feed()

    def _create_data_feed(self):
        if self.source.lower() == "tushare":
            return TuShareDataFeed(self.token)
        elif self.source.lower() == "yahoo":
            return YahooFinanceDataFeed(self.token)
        else:
            raise ValueError(f"Unsupported data source: {self.source}")

    def fetch_daily_data(self, symbol: str, start_date: str, end_date: str):
        """获取日线数据"""
        return self._data_feed.fetch_daily_data(symbol, start_date, end_date)

    def fetch_minute_data(self, symbol: str, start_date: str, end_date: str):
        """获取分钟线数据"""
        return self._data_feed.fetch_minute_data(symbol, start_date, end_date)

    def fetch_current_data(self, symbol: str):
        """获取当前数据"""
        return self._data_feed.fetch_current_data(symbol)
