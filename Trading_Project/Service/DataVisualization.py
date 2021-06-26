from Trading_Project.Financial_Tools.Tools.Portfolio import Portfolio
from Trading_Project.Financial_Tools.Tools.MySeries import MySeries
from Trading_Project.Service.BinanceDownloader import BinanceDownloader
from Trading_Project.Service import path
from pandas import DataFrame, Series
from datetime import datetime
import numpy as np


class DataVisualization(object):

    """It's a service only for Portfolio performance and its assets visualization..."""

    def __init__(self, Portfolio_obj: 'class instance', prices: DataFrame):
        self.Portfolio = Portfolio_obj
        self.prices = prices[self.Portfolio.assets] if isinstance(prices, DataFrame) else TypeError

    def _index_computing_for_assets(self, statistics_period: int):
        last_prices = self.prices[-statistics_period:]  # pd.Series
        self._assets_last_tot_ret = last_prices.iloc[-1] / last_prices.iloc[0] - 1  # pd.Series
        self._assets_last_avg_ret = last_prices.pct_change().mean()
        self._assets_last_std_ret = last_prices.pct_change().std()  # pd.Series
        self._assets_sharpe_ratio = last_prices.pct_change().mean() / self._assets_last_std_ret

        self._assets_calmar_ratio = {}
        for coin in last_prices.columns:
            s = MySeries(list(last_prices[coin].dropna()), is_returns=False)
            self._assets_calmar_ratio[coin] = s.calmar_ratio()

    def _index_computing_for_portfolio(self):
        Portfolio = self.Portfolio
        # if Portfolio was just instanciate, there's no way to evaluate the performance
        if len(Portfolio.history_value) > 1:
            self._port_last_ret = Portfolio.history_value[-1] / Portfolio.history_value[-2]
            self._port_avg_ret = MySeries(Portfolio.history_value, is_returns=False).avg_ret()
            self._port_std_ret = MySeries(Portfolio.history_value, is_returns=False).standard_deviation()\
                                    if len(Portfolio.history_value) > 2 else 0  # I need at least 3 price to get 2 ret
            self._port_sharpe = MySeries(Portfolio.history_value, is_returns=False).sharpe_ratio()\
                                    if len(Portfolio.history_value) > 2 else 0  # I need at least 3 price to get 2 ret
            self._port_calmar = MySeries(Portfolio.history_value, is_returns=False).calmar_ratio()
            self._port_turnover = Portfolio.turnover()
        else:
            return None

    def assets_summary_visualization(self, statistics_period, data_frequency: 'int: obs per day'):

        DataVisualization._index_computing_for_assets(self, statistics_period=statistics_period)
        now = datetime.now()

        print('\n******************* ASSETS SUMMARY *******************\n')
        print(f'Evaluation date  : {now.year}/{now.month}/{now.day} at {now.hour}:{now.minute}')
        print(f'Upgrade from     : last {round(statistics_period/data_frequency)} days')
        print(f'Data frequency   : {data_frequency} records per day')
        print(' ')
        print('TOTAL RETURN:')
        for coin in self.prices:
            print(f'                 - {coin} --> {round(self._assets_last_tot_ret[coin] * 100, 2)} %')
        print('AVERAGE RETURNS:')
        for coin in self.prices:
            print(f'                 - {coin} --> {round(self._assets_last_avg_ret[coin] * 100, 2)} %')
        print('STANDARD DEVIATION:')
        for coin in self.prices:
            print(f'                 - {coin} --> {round(self._assets_last_std_ret[coin] * 100, 2)} %')
        print('SHARPE RATIO:')
        for coin in self.prices:
            print(f'                 - {coin} --> {round(self._assets_sharpe_ratio[coin] * 100, 2)} %')
        print('CALMAR RATIO:')
        for coin in self.prices:
            if self._assets_calmar_ratio[coin] != None:
                print(f'                 - {coin} --> {round(self._assets_calmar_ratio[coin] * 100, 2)} %')
            else:
                print(f'                 - {coin} --> N/A')
        print('\n******************************************************')

    def portfolio_summary_visualization(self, frequency_upgrade: 'str'):
        Portfolio = self.Portfolio
        DataVisualization._index_computing_for_portfolio(self)
        now = datetime.now()

        if len(Portfolio.history_value) > 1:
            print('\n************** PORTFOLIO PERFORMANCE **************\n')
            print(f'Evaluation date  : {now.year}/{now.month}/{now.day} at {now.hour}:{now.minute}')
            print(f'Evaluation period: last {len(Portfolio.history_value) - 1} {frequency_upgrade}')
            print(f'Data frequency   : {frequency_upgrade}')
            print('  ')
            print(f'TOTAL RETURN       : {round((Portfolio.history_value[-1] / Portfolio.history_value[0] - 1)*100, 3)} %')
            print(f'LAST PERIOD RETURN : {round(self._port_last_ret * 100, 2)} %')
            print(f'AVERAGE RETURN     : {round(self._port_avg_ret * 100, 2)} %')
            if self._port_std_ret != 0:
                print(f'STANDARD DEVIATION : {round(self._port_std_ret * 100, 2)} %')
            else:
                print(f'STANDARD DEVIATION : N/A')
            if self._port_sharpe != 0:
                print(f'SHARPE RATIO       : {round(self._port_sharpe * 100, 2)} %')
            else:
                print(f'SHARPE RATIO       : N/A')
            if self._port_calmar != None:
                print(f'CALMAR RATIO       : {round(self._port_calmar * 100, 2)} %')
            else:
                print(f'CALMAR RATIO       : N/A')
            print(f'TURNOVER           : {round(self._port_turnover, 2)} ')
            print('\n***************************************************')
        else:
            print('\nPORTFOLIO HAS JUST BEEN INSTANTIATED --> there are no available statistics :(')
