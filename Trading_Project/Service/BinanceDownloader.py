import numpy as np
import pandas as pd
import csv
import requests


class BinanceDownloader(object):
    def __init__(self,
                 URL: 'str list',
                 folder_path: str,
                 start_name_URL: int,  # first letter of the coin name position in the URL
                 end_name_URL: str  # symbol (letter, _, ...) after the last letter of the coin name in the URL
                 ):
        self.URL = URL
        self.folder_path = folder_path
        self.start_name_URL = start_name_URL
        self.end_name_URL = end_name_URL
        self.coin_names = BinanceDownloader.__set_coin_names(self)
        self.coins_path = BinanceDownloader.__set_path_name(self)
        self.dataframe_list = None
        self.specific_dataframe = None
        self.__csv_stored = False

    def __set_coin_names(self):
        # get the coin_names from the URL and set them into the self function's arguments
        coin_names = []
        for url in self.URL:
            letters = self.start_name_URL
            name = ''
            while url[letters] != self.end_name_URL:
                name = name + url[letters]
                letters += 1
            # name = '/USDT'.join(name.split(sep='USDT')) # to embellish the name a little bit...
            coin_names.append(name)

        return coin_names

    def __set_path_name(self):
        # Create a path directory for each coin and store them into the self function's arguments
        coins_path = [(self.folder_path + coin_name) for coin_name in self.coin_names]
        return coins_path

    def store_csv(self):
        from requests.packages.urllib3.exceptions import InsecureRequestWarning

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        index_name = 0
        for url in self.URL:
            response = requests.get(url, verify=False)

            with open(self.coins_path[index_name] + '.csv', 'w') as f:
                writer = csv.writer(f)
                for line in response.iter_lines():
                    writer.writerow(line.decode('utf-8').split(','))
            index_name += 1
        self.__csv_stored = True

    # def read_csv_from_URL(self):
    #     # READ CSV FROM URL. There's an issue: the DataFrames output have all the data into one column.. Fix it!
    #     data_set = [pd.read_csv(url) for url in self.URL]
    #     return data_set
    #
    # def store_csv(self):
    #     # SAVE ALL THE DATA FRAME AS CSV in a folder (the folder is temporary)
    #     coins_path = BinanceDownloader.set_path_name(self)
    #     data_set = BinanceDownloader.read_csv_from_URL(self)
    #     index_name = 0
    #     for coin in data_set:
    #         coin.to_csv(coins_path[index_name] + '.csv')
    #         index_name += 1

    def create_dataframe_list(self,
                              header: int = 1,
                              **kwargs
                              ):

        if self.__csv_stored:
            self.dataframe_list = [pd.read_csv(coin_path + '.csv',
                                               header=header,
                                               **kwargs
                                               ) for coin_path in self.coins_path]
        else:
            self.dataframe_list = [pd.read_csv(url,
                                               header=header,
                                               **kwargs
                                               ) for url in self.URL]
        return self.dataframe_list

    def create_specific_dataframe(self,
                                  target_column: str,
                                  index_name: str = 'date',
                                  reverse: bool = True,
                                  **kwargs  # **kwargs: other args for import DataFrame using create_dataframe_list
                                  ) -> 'DataFrame object':
        """Returns a DataFrame with specific columns.
        ATTENTION: the index which you put have to be the longest of the dataframe. Check the URL passed at the first
        instance of BinanceDownloader e put the url which cointains the longest series at the first position."""

        dataframe_list = BinanceDownloader.create_dataframe_list(self,
                                                                 usecols=[index_name, target_column],
                                                                 **kwargs
                                                                 )
        specific_dataframe = dataframe_list[0].\
                                                rename(columns={target_column:self.coin_names[0]}).\
                                                set_index(index_name)
        idx_name = 1
        for coin in dataframe_list[1:]:
            specific_dataframe = specific_dataframe.join(coin.\
                                                                rename(columns={target_column: self.coin_names[idx_name]}).\
                                                                set_index(index_name))
            idx_name += 1

        if reverse:
            self.specific_dataframe = specific_dataframe.reindex(specific_dataframe.index[::-1])
            return self.specific_dataframe
        else:
            self.specific_dataframe = specific_dataframe
            return self.specific_dataframe

    def dataframe_log_returns(self,
                              prices_column_name: str = 'close',
                              index_name: str = 'date',
                              **kwargs
                              ):

        if self.specific_dataframe is None:
            dataframe = BinanceDownloader.create_specific_dataframe(self, target_column=prices_column_name,
                                                                    index_name=index_name, **kwargs)
        else:
            dataframe = self.specific_dataframe

        # APPLY E' LENTA, PROVARE AD USARE EVAL O FARE DIRETTAMENTE IL LOG
        coin_log_ret = dataframe.apply(lambda x: np.log(x)).diff(periods=-1)
        coin_log_ret = coin_log_ret.drop(dataframe.index[-1])

        return coin_log_ret
