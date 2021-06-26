import datetime

from Trading_Project.Financial_Tools.__init__ import *
from pandas import DataFrame

Portfolio = Tools.Portfolio.Portfolio
Ranker = Tools.ranking.Ranker


class TradingSystem(object):

    def __init__(self,
                 dataframe: DataFrame, is_returns: bool
                 ):
        self.dataframe = dataframe if isinstance(dataframe, DataFrame) else TypeError
        self._is_returns = is_returns

    def _ranking_method_choice(self,
                               ranking_method: str,
                               best: int,
                               ranking_periods=None,
                               last=True,
                               rolling=None
                               ):

        ranker = Tools.ranking.Ranker(dataframe=self.dataframe, is_returns=self._is_returns)
        if ranking_method == 'returns':
            assets = ranker.ranking_by_returns(ranking_periods=ranking_periods,
                                               best=best,
                                               last=last
                                               )
        elif ranking_method == 'ma':
            assets = ranker.ranking_by_moving_average(rolling=rolling,
                                                      best=best
                                                      )
        elif ranking_method == 'returns, ma':
            assets = ranker.ranking_by_returns_and_ma(rolling=rolling,
                                                      ranking_periods=ranking_periods,
                                                      best=best,
                                                      last=last
                                                      )
        else:
            raise TypeError('You have choosen a ranking_method that no exists!')

        if assets:
            return assets
        else:
            return None

    def portfolio_building(self,
                           starting_value: 'int, float',
                           ranking_method: str,
                           best: int,
                           ranking_periods=None,
                           last=True,
                           rolling=None
                           ):

        assets = TradingSystem._ranking_method_choice(self,
                                                      ranking_method=ranking_method,
                                                      best=best,
                                                      ranking_periods=ranking_periods,
                                                      last=last,
                                                      rolling=rolling
                                                      )

        self.portfolio = Tools.Portfolio.Portfolio(starting_value=starting_value,
                                                   assets=assets,
                                                   date=self.dataframe.index[-1]
                                                   )

    def portfolio_rebalancing(self, new_prices: DataFrame,
                              is_returns: bool,
                              time_passed: int,
                              ranking_method: str,
                              best: int,
                              ranking_periods: int = None,
                              last: bool = True,
                              rolling: int = None,
                              bid_ask_spread: 'int, float' = None
                              ):

        self.dataframe = new_prices
        self._is_returns = is_returns

        new_assets = TradingSystem._ranking_method_choice(self,
                                                          ranking_method=ranking_method,
                                                          best=best,
                                                          ranking_periods=ranking_periods,
                                                          last=last,
                                                          rolling=rolling
                                                          )

        self.portfolio.rebalancing(new_assets=new_assets,
                                   new_prices=new_prices,
                                   time_passed=time_passed,
                                   bid_ask_spread=bid_ask_spread
                                   )

    #
    # def portfolio_rebalancing(self, ranking_method, best: int, new_prices: DataFrame, is_returns=False,
    #                           ranking_periods=None, rolling=None, bid_ask_spread=None, last=True):
    #
    #     self._Ranker = Ranking(dataframe=new_prices, is_returns=is_returns)
    #     new_assets = TradingSystem._ranking_method_choice(self,
    #                                                       ranking_method=ranking_method,
    #                                                       best=best, ranking_periods=ranking_periods,
    #                                                       last=last, rolling=rolling)
    #     self.portfolio.rebalancing(
    #                                new_assets=new_assets,
    #                                new_prices=new_prices,
    #                                bid_ask_spread=bid_ask_spread)
    #     return self.portfolio
