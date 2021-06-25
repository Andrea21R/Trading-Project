import numpy as np
import pandas as pd
from pandas import Series, DataFrame


class Portfolio(object):
    """Class to build and manage an equally-weighted portfolio"""

    def __init__(self, starting_value: int, assets: 'string list'):
        self.value = starting_value
        self.history_value = [self.value]
        self.assets = assets
        self.allocation = {key: value for (key, value) in zip(assets, [self.value / len(assets)] * len(assets))}
        self.history_returns = []
        self.history_profit_loss = []

    def _asset_turnover(self, new_assets: 'string list'):
        new = []
        hold = []
        for asset in new_assets:
            if asset in self.assets:
                hold.append(asset)
            else:
                new.append(asset)
        off = [asset for asset in self.assets if not(asset in new_assets)]

        return {'new': new, 'hold': hold, 'off': off}

    def _upgrade_returns(self, new_prices: DataFrame):

        if isinstance(new_prices, DataFrame):
            ret_assets = [asset for asset in new_prices.columns if asset in self.assets]
            self.history_returns = ((new_prices.iloc[-1] / new_prices.iloc[0]) - 1)[ret_assets]
            # upgrade the positions, then in rebalancing() I'll set them to the newest
            self.allocation = {key: value * (1 + self.history_returns[key])
                               for (key, value) in zip(self.allocation.keys(),
                                                            self.allocation.values())}
            self.value = sum(self.allocation.values())
        else:
            raise TypeError("Input have to be a DataFrame object!")

    def rebalancing(self, new_assets: 'string list', new_prices, bid_ask_spread=None):
        """in "new_prices" remember to insert also the last_price before the last re-balancing or the first building"""
        old_allocation = self.allocation
        Portfolio._upgrade_returns(self, new_prices=new_prices)
        # find the not corresponding extra-allocation according by the equally-weighted approach
        extra_allocation = {asset: (value/self.value - 1/len(self.assets))
                            for (asset, value) in self.allocation.items()}

        asset_turnover = Portfolio._asset_turnover(self, new_assets=new_assets)
        position_off = {}
        profit_loss = {}
        old_to_rebalance = {}
        for (asset, value, extra_value) in zip(self.allocation.keys(),
                                               self.allocation.values(),
                                               extra_allocation.values()):

            if asset in asset_turnover['off']:
                position_off[asset] = value
                profit_loss[asset] = old_allocation[asset] * self.history_returns[asset]

            if (asset in asset_turnover['hold']):
                old_to_rebalance[asset] = value * np.abs(extra_value)
                profit_loss[asset] = value * self.history_returns[asset]

        new_position = {key: self.value * 1 / len(new_assets)
                            for key in asset_turnover['new']}

        if bid_ask_spread:
            transaction_cost = (bid_ask_spread/2) * (sum(position_off.values()) +
                                            sum(old_to_rebalance.values()) +
                                            sum(new_position.values()))
            self.value -= transaction_cost
            profit_loss['transaction_cost'] = -transaction_cost

        self.allocation = {key: value for (key, value)
                           in zip(new_assets, [self.value / len(new_assets)] * len(new_assets))}
        self.history_value.append(self.value)
        self.history_profit_loss.append(profit_loss)
        self.assets = new_assets

        # position value of the assets which I have to REMOVE FROM PORTFOLIO
        # position_off = sum({self.allocation[key]
        #                    for key in self.allocation.keys()
        #                    if key in asset_turnover['over']})
        # profits from assets which have got an extra gain over the starting position value
        # profit = sum({self.allocation[key] * extra_value
        #                    for (key, extra_value) in zip(self.allocation.keys(), extra_allocation.values())
        #                    if (key in asset_turnover['hold'])   and   (extra_value > 0)})
        # position value for the new assets which I have to put into portfolio


        # loss_position = sum({self.allocation[key] * np.abs(extra_value)
        #                    for (key, extra_value) in zip(self.allocation.keys(), extra_allocation.values())
        #                    if (key in asset_turnover['hold'])   and   (extra_value < 0)})
        # total transaction cost from rebalancing:
        # 1) I have to pay for closing the off positions
        # 2) I have to pay for closing the part of positions related to the profits (equally-weighted approach)
        # 3) I have to pay for opening the new positions related to the new-entry assets
        # 4) I have to pay for restoring the assets in loss which I want to hold into the portfolio






