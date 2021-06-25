import pandas as pd
from pandas import Series, DataFrame


class Ranker(object):

    def __init__(self, dataframe: DataFrame, is_returns: bool):
        self.__is_returns = is_returns
        self.prices = dataframe if not(is_returns) else None
        self.returns = Ranker.__ret(self, dataframe)

    def __ret(self, dataframe):
        if isinstance(dataframe, DataFrame):
            if self.__is_returns:
                return dataframe
            else:
                return dataframe.pct_change().dropna()
        else:
            raise TypeError("Input have to be a DataFrame object!")

    def _moving_average(self, rolling, plot=False):
        """Computes a simple moving average(SMA) for a given dataframe"""
        ma = self.prices.rolling(rolling).mean()

        if plot:
            ma_clear = ma.dropna()
            ma_clear.divide(ma_clear.iloc[0]).plot()
            return ma
        else:
            return ma

    def ranking_by_returns(self, ranking_periods, last=True):
        """Ranking returns a list sorted in descending order by evaluating the elements according to the given key."""
        if last:
            return (((self.returns.iloc[-ranking_periods:] + 1).\
                                                                cumprod()).iloc[-1]).\
                                                                sort_values(ascending=False)
        else:
            return (((self.returns.iloc[:ranking_periods] + 1).\
                                                                cumprod()).iloc[-1]).\
                                                                sort_values(ascending=False)

    def ranking_by_moving_average(self, rolling):
        moving_average = Ranker._moving_average(self, rolling=rolling)
        return (self.prices.iloc[-1].divide(moving_average.iloc[-1]) - 1).\
                                                                            sort_values(ascending=False)

    def ranking_by_returns_and_ma(self, rolling, ranking_periods, best: int) -> 'string list':
        if not isinstance(best, int):
            raise ValueError('Best has to be an int. Tips: round it before using the function')

        moving_average = Ranker._moving_average(self, rolling=rolling)
        ranking_by_returns = Ranker.ranking_by_returns(self, ranking_periods=ranking_periods)

        above_ma = self.prices.iloc[-1] > moving_average.iloc[-1]

        top = [coin for coin in list(above_ma[above_ma == True].index)
                    if coin in list(ranking_by_returns.index)]
        # It would manages the situation where there aren't assets which match both the ranking
        if not top:
            raise ValueError("There aren't asset that match both the moving average ranking and the returns ranking" )
        else:
            return top[:best]




