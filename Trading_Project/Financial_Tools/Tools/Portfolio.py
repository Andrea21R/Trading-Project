import numpy as np
import pandas as pd
from pandas import Series, DataFrame
from datetime import datetime

class Portfolio(object):
    """Class to build and manage an equally-weighted portfolio"""

    def __init__(self,
                 starting_value: int or float,
                 assets: 'string list',
                 date: datetime or str
                 ):

        self.operation_dates = [date]
        self.value = starting_value
        self.history_value = [self.value]
        self.assets = assets
        self.allocation = {key: value for (key, value) in zip(assets, [self.value / len(assets)] * len(assets))}\
                            if assets else {}
        self.history_prices = []
        self.history_returns = []
        self.history_profit_loss = []
        # for turnover computing
        self.buy = starting_value
        self.sell = 0

    def _asset_turnover(self,
                        new_assets: 'string list'
                        ):
            new = []
            hold = []
            for asset in new_assets:
                if asset in self.assets:
                    hold.append(asset)
                else:
                    new.append(asset)
            off = [asset for asset in self.assets if not(asset in new_assets)]

            return {'new': new, 'hold': hold, 'off': off}

    def _upgrade_returns(self,
                         new_prices: DataFrame,
                         time_passed: int
                         ):

        if isinstance(new_prices, DataFrame):
            ret_assets = [asset for asset in new_prices.columns if asset in self.assets]
            self.history_prices.append(new_prices[ret_assets])
            self.history_returns.append(((new_prices.iloc[-1] / new_prices.iloc[-time_passed]) - 1)[ret_assets])
            # upgrade the positions, then in rebalancing() I'll set them to the newest
            self.allocation = {key: value * (1 + self.history_returns[-1][key])
                               for (key, value) in zip(self.allocation.keys(),
                                                       self.allocation.values())}
            self.value = sum(self.allocation.values())
        else:
            raise TypeError("Input have to be a DataFrame object!")

    def rebalancing(self,
                    new_assets: 'string list',
                    new_prices: DataFrame,
                    time_passed: int,
                    bid_ask_spread: int or float = None
                    ):
        """in "new_prices" remember to insert also the last_price before the last re-balancing or the first building"""

        old_allocation = self.allocation
        self.operation_dates.append(new_prices.index[-1])
        Portfolio._upgrade_returns(self,
                                   new_prices=new_prices,
                                   time_passed=time_passed
                                   )
        # find the not corresponding extra-allocation according by the equally-weighted approach
        extra_allocation = {asset: (value/self.value - 1/len(self.assets))
                            for (asset, value) in self.allocation.items()}

        asset_turnover = Portfolio._asset_turnover(self,
                                                   new_assets=new_assets
                                                   )
        position_off = {}
        profit_loss = {}
        old_to_rebalance = {}
        for (asset, value, extra_value) in zip(self.allocation.keys(),
                                               self.allocation.values(),
                                               extra_allocation.values()):

            if asset in asset_turnover['off']:
                position_off[asset] = value
                profit_loss[asset] = old_allocation[asset] * self.history_returns[-1][asset]
                self.sell += value

            if (asset in asset_turnover['hold']):
                old_to_rebalance[asset] = value * np.abs(extra_value)
                profit_loss[asset] = value * self.history_returns[-1][asset]

        new_position = {key: self.value * 1 / len(new_assets)
                            for key in asset_turnover['new']}
        self.sell += sum(new_position.values())

        if bid_ask_spread:
            transaction_cost = (bid_ask_spread/2) * (sum(position_off.values()) +
                                                     sum(old_to_rebalance.values()) +
                                                     sum(new_position.values()))
            self.value -= transaction_cost
            profit_loss['transaction_cost'] = -transaction_cost

        self.allocation = {key: value for (key, value)
                           in zip(new_assets,
                                  [self.value / len(new_assets)] * len(new_assets)
                                  )}
        self.history_value.append(self.value)
        self.history_profit_loss.append(profit_loss)
        self.history_profit_loss[-1]['date'] = self.operation_dates[-1]
        self.assets = new_assets

    def turnover(self):
        return min(self.buy, self.sell) / np.mean(self.history_value)






