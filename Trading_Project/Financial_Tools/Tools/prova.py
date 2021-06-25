from ranking import Ranker
from Trading_Project.Service import path, BinanceDownloader
from Portfolio import Portfolio
import random as rnd

Downloader = BinanceDownloader.BinanceDownloader(path.URL[0:20],
                                                 start_name_URL=path.start_name_URL,
                                                 end_name_URL=path.end_name_URL,
                                                 folder_path=path.folder_path)
price = Downloader.create_specific_dataframe(target_column='close', index_name='date', reverse=True)
price_pre = price.iloc[:-7*24]
price_post = price.iloc[-7*24-1:]

ranker = Ranker(price_pre, is_returns=False)
week_ranking = ranker.ranking_by_returns(ranking_periods=24*7)
SMA = ranker._moving_average(rolling=7*30)
SMA_ranking = ranker.ranking_by_moving_average(rolling=24*30)
# double_ranking = ranker.ranking_by_returns_and_ma(rolling=24*30, ranking_periods=24*7, best=3)
top_pre = []
top_post = []
for i in range(3):
    top_pre.append(Downloader.coin_names[rnd.randrange(1, len(Downloader.URL))])
    top_post.append(Downloader.coin_names[rnd.randrange(1, len(Downloader.URL))])

Portfolio = Portfolio(10_000, top_pre)
Portfolio.rebalancing(new_assets=top_post, new_prices=price_post, bid_ask_spread=0.0015)

