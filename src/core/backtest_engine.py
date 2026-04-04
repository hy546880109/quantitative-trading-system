"""
回测引擎模块
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime


class BacktestEngine:
    """
    回测引擎类
    """

    def __init__(self, initial_capital: float = 10000):
        """
        初始化回测引擎
        :param initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.portfolio = {}  # 持仓信息 {symbol: quantity}
        self.cash = initial_capital
        self.trades = []  # 交易记录
        self.equity_curve = []  # 资金曲线

    def reset(self):
        """重置回测引擎状态"""
        self.current_capital = self.initial_capital
        self.portfolio = {}
        self.cash = self.initial_capital
        self.trades = []
        self.equity_curve = []

    def execute_trade(self, symbol: str, signal: int, price: float, date: str):
        """
        执行交易
        :param symbol: 交易标的
        :param signal: 交易信号 (1=买入, -1=卖出, 0=持有)
        :param price: 当前价格
        :param date: 当前日期
        """
        if signal == 1:  # 买入信号
            # 计算可买入数量 (使用95%的资金，保留5%作为缓冲)
            available_cash = self.cash * 0.95
            if available_cash > price:
                quantity = int(available_cash / price)
                if quantity > 0:
                    cost = quantity * price
                    self.cash -= cost
                    self.portfolio[symbol] = self.portfolio.get(symbol, 0) + quantity

                    # 记录交易
                    self.trades.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'BUY',
                        'quantity': quantity,
                        'price': price,
                        'total': cost
                    })

        elif signal == -1:  # 卖出信号
            if symbol in self.portfolio and self.portfolio[symbol] > 0:
                quantity = self.portfolio[symbol]
                proceeds = quantity * price
                self.cash += proceeds
                self.portfolio[symbol] = 0

                # 记录交易
                self.trades.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': quantity,
                    'price': price,
                    'total': proceeds
                })

    def calculate_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        计算当前投资组合价值
        :param current_prices: 当前价格字典
        :return: 投资组合总价值
        """
        total_value = self.cash
        for symbol, quantity in self.portfolio.items():
            if quantity > 0 and symbol in current_prices:
                total_value += quantity * current_prices[symbol]
        return total_value

    def run_backtest(self, strategy, data: pd.DataFrame, symbol: str = "TEST") -> Dict[str, Any]:
        """
        运行回测
        :param strategy: 交易策略对象
        :param data: 包含OHLCV数据的DataFrame
        :param symbol: 交易标的名称
        :return: 回测结果字典
        """
        self.reset()

        # 确保数据包含必要的列
        required_columns = ['close', 'high', 'low']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"数据缺少必要的列: {col}")

        # 生成交易信号
        signals = strategy.generate_signals(data)

        # 逐日执行交易
        for i, (idx, row) in enumerate(data.iterrows()):
            if i >= len(signals):
                break

            current_signal = signals.iloc[i]
            current_price = row['close']
            current_date = str(idx) if not isinstance(idx, str) else idx

            # 执行交易
            self.execute_trade(symbol, current_signal, current_price, current_date)

            # 计算并记录当前投资组合价值
            portfolio_value = self.calculate_portfolio_value({symbol: current_price})
            self.equity_curve.append({
                'date': current_date,
                'portfolio_value': portfolio_value,
                'cash': self.cash,
                'holdings': self.portfolio.get(symbol, 0) * current_price
            })

        # 计算回测指标
        final_value = self.calculate_portfolio_value({symbol: data.iloc[-1]['close']})
        total_return = (final_value - self.initial_capital) / self.initial_capital

        # 计算夏普比率
        returns = self._calculate_returns()
        sharpe_ratio = self._calculate_sharpe_ratio(returns)

        # 计算最大回撤
        max_drawdown = self._calculate_max_drawdown()

        # 统计交易次数
        buy_trades = len([t for t in self.trades if t['action'] == 'BUY'])
        sell_trades = len([t for t in self.trades if t['action'] == 'SELL'])

        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(self.trades),
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'equity_curve': self.equity_curve,
            'trades': self.trades
        }

    def _calculate_returns(self) -> List[float]:
        """
        计算收益率序列
        :return: 收益率列表
        """
        if len(self.equity_curve) < 2:
            return []

        returns = []
        for i in range(1, len(self.equity_curve)):
            prev_value = self.equity_curve[i - 1]['portfolio_value']
            curr_value = self.equity_curve[i]['portfolio_value']
            if prev_value > 0:
                returns.append((curr_value - prev_value) / prev_value)
            else:
                returns.append(0)

        return returns

    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.03) -> float:
        """
        计算夏普比率
        :param returns: 收益率列表
        :param risk_free_rate: 无风险利率 (年化)
        :return: 夏普比率
        """
        if not returns or len(returns) < 2:
            return 0.0

        returns_array = np.array(returns)

        # 计算平均收益率和标准差 (年化)
        mean_return = np.mean(returns_array) * 252  # 假设252个交易日
        std_return = np.std(returns_array) * np.sqrt(252)

        if std_return == 0:
            return 0.0

        # 计算夏普比率
        sharpe = (mean_return - risk_free_rate) / std_return
        return sharpe

    def _calculate_max_drawdown(self) -> float:
        """
        计算最大回撤
        :return: 最大回撤 (百分比)
        """
        if len(self.equity_curve) < 2:
            return 0.0

        peak = self.equity_curve[0]['portfolio_value']
        max_drawdown = 0.0

        for point in self.equity_curve:
            current_value = point['portfolio_value']

            # 更新峰值
            if current_value > peak:
                peak = current_value

            # 计算当前回撤
            if peak > 0:
                drawdown = (peak - current_value) / peak
                max_drawdown = max(max_drawdown, drawdown)

        return max_drawdown * 100  # 转换为百分比