from pandas import DataFrame

def dataset_simulation(dataset: DataFrame, rolling: int):
    dataset.dropna(inplace=True)
    roll = rolling
    dataset_simu = [dataset.iloc[:roll*5]]
    for week in range(6, round(len(dataset)/roll) - 6):
        dataset_simu.append(dataset.iloc[: roll * (week + 1)])
    return dataset_simu

def date_list_simulation(dataset: DataFrame, rolling: int):
    dataset.dropna(inplace=True)
    roll = rolling
    date = [dataset.iloc[:roll*5].index[-1][:11]]

    for week in range(6, round(len(dataset)/roll) - 6):
        date.append(dataset.iloc[: roll * (week + 1)].index[-1][:11])
    return date
