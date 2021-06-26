from Trading_Project.Financial_Tools import TradingSystem
from Trading_Project.Service import BinanceDownloader, path,\
                                    backtesting_date_simulation, \
                                    DataVisualization
import matplotlib.pylab as plt

BinanceDownloader = BinanceDownloader.BinanceDownloader
DataVisualization = DataVisualization.DataVisualization
dataset_simulation = backtesting_date_simulation.dataset_simulation
date_list_simulation = backtesting_date_simulation.date_list_simulation

# Get the data
Downloader = BinanceDownloader(path.URL,start_name_URL=path.start_name_URL,
                                             end_name_URL=path.end_name_URL,
                                             folder_path=path.folder_path
                                            )
price = Downloader.create_specific_dataframe(target_column='close', index_name='date', reverse=True)
# clean the data: 1) remove all NaN; 2) remove too short series
for coin in price.columns:
    if price[coin].dropna().__len__() < 7838:
        del price[coin]
# create the dataset for back-testing
dataset = dataset_simulation(price, rolling=7*24)
dates = date_list_simulation(price, rolling=7*24)


# Instantiate the TradingSystem object
trading_system = TradingSystem.TradingSystem(dataframe=dataset[0], is_returns=False)
# How many asset I want into the portfolio?
best = round(len(price.columns) * 0.15)
# building portfolio
trading_system.portfolio_building(starting_value=1_000_000, ranking_method='returns, ma', best=best,
                                  ranking_periods=24*7, rolling=24*30)
# data visualization
visualizer = DataVisualization(Portfolio_obj=trading_system.portfolio, prices=dataset[0])
visualizer.assets_summary_visualization(statistics_period=len(dataset[0]), data_frequency=24)


# back-testing
for week in dataset[1:]:
    trading_system.portfolio_rebalancing(new_prices=week, is_returns=False,
                                     time_passed=7*24,
                                     ranking_method='returns, ma', best=best,
                                     ranking_periods=24*7, rolling=24*30, bid_ask_spread=0.0015)
# data visualization
visualizer = DataVisualization(Portfolio_obj=trading_system.portfolio, prices=dataset[-1])
visualizer.assets_summary_visualization(statistics_period=len(dataset[-1]), data_frequency=24)
visualizer.portfolio_summary_visualization(frequency_upgrade='monthly')
# graph portfolio value
normalized_value = [x / 1_000_000 for x in trading_system.portfolio.history_value]
plt.figure()
plt.plot(dates, normalized_value)
plt.grid()
plt.title("PORTFOLIO PATH", fontweight="bold")
plt.figtext(0.31, 0.8, f'Starting Value :  $ {round(trading_system.portfolio.history_value[0])}', fontweight='bold')
plt.figtext(0.31, 0.775, f'Final Value     :  $ {round(trading_system.portfolio.history_value[-1])}', fontweight='bold')
plt.figtext(0.31, 0.75, f'TOTAL RETURN  : {round(trading_system.portfolio.history_value[-1]/trading_system.portfolio.history_value[0]*100,2)} %', fontweight='bold')
plt.ylabel('Millions of $')


def merge_heterogeneous_dicts(dict1, dict2):
    key_sum = set(list(dict1.keys()) + list(dict2.keys()))
    key_common = [key for key in list(dict1.keys()) if key in list(dict2.keys())]
    key_not_common = [key for key in key_sum if not (key in key_common)]

    final = {key: dict1[key] + dict2[key] for key in key_sum if key in key_common}  # common keys
    for key in key_not_common:
        final[key] = dict1[key] if key in list(dict1.keys()) else dict2[key]  # not common keys

    return final

for count in range(len(trading_system.portfolio.history_profit_loss) - 1):

    if count == 0:
        dict1 = trading_system.portfolio.history_profit_loss[0].copy()
        del dict1['date']
        dict2 = trading_system.portfolio.history_profit_loss[1].copy()
        del dict2['date']
        final = merge_heterogeneous_dicts(dict1, dict2)
    else:
        dict1 = final.copy()
        dict2 = trading_system.portfolio.history_profit_loss[count + 1].copy()
        del dict2['date']
        final = merge_heterogeneous_dicts(dict1, dict2)
# graph profit/loss
plt.figure()
value_reduced = [value/100_000 for value in list(final.values())]
plt.bar(final.keys(), value_reduced)
plt.ylabel('Values x100.000')
plt.title('PROFIT/LOSS TRADING STRATEGY', fontweight='bold')
plt.xticks(rotation=50)


# print('THE END...')
