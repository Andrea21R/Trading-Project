from collections.abc import Iterable
from statistics import stdev, mean


class MySeries(object):

    def __init__(self, series, is_returns=True):
        self.__is_returns = is_returns
        self.series = MySeries.__set_series(self, series)

    def __repr__(self):
        return f'Series: {self.series}'

    def __getitem__(self, item):
        return self.series[item]

    def __setitem__(self, key, value):
        self.series[key] = [*value]  # make tests

    def __delitem__(self, key):
        del self.series[key]

    def append(self, value):
        if isinstance(value, (int, float)):
            self.series.append(value)
        else:
            raise TypeError("You can only add a single int or float type. \n"
                            "           For iterables, which aren't str or dict, try to use extend() method")

    def insert(self, position, value):
        if isinstance(value, (int, float)):
            return self.series.insert(position, value)
        else:
            raise TypeError("You can only add a single int or float type. \n"
                            "           For iterables, which aren't str or dict, try to use extend() method")

    def extend(self, values):
        if isinstance(values, (str, dict)):
            raise TypeError("You cannot add str or dict...")

        elif isinstance(values, MySeries):
            return self.series.extend(values.series)

        elif not isinstance(values, Iterable):
            raise TypeError("extend() method is only for iterables or MySeries objects.\n"
                            "           To add a single (numeric) element use append() method instead...")
        else:
            return self.series.extend(list(values))

    def pop(self, value):
        return self.series.pop(value)

    def __len__(self):
        return len(self.series)

    def __eq__(self, other):
        if isinstance(other, MySeries):
            return self.series == other.series
        else:
            raise TypeError(f"{other} isn't an instance of MySeries")

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return MySeries([self.series[i] + other for i in range(len(self.series))])

        elif not (isinstance(other, (MySeries, Iterable))) or isinstance(other, (str, dict)):
            raise TypeError("You have inserted a wrong input type...")

        elif len(other) != len(self.series):
            raise ValueError("the lengths aren't the same")
        # If I didn't have problem with types or other is a single number, then do the addition
        else:
            return MySeries([self.series[i] + other[i] for i in range(len(self.series))])

    def __iadd__(self, other):
        return MySeries.__add__(self, other)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return MySeries([self.series[i] - other for i in range(len(self.series))])

        elif not (isinstance(other, (MySeries, Iterable))) or isinstance(other, (str, dict)):
            raise TypeError("You have inserted a wrong input type...")

        elif len(other) != len(self.series):
            raise ValueError("the lengths aren't the same")
        # If I didn't have problem with types or other is a single number, then do the addition
        else:
            return MySeries([self.series[i] - other[i] for i in range(len(self.series))])

    def __isub__(self, other):
        return MySeries.__sub__(self, other)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return MySeries([self.series[i] * other for i in range(len(self.series))])

        elif not (isinstance(other, (MySeries, Iterable))) or isinstance(other, (str, dict)):
            raise TypeError("You have inserted a wrong input type...")

        elif len(other) != len(self.series):
            raise ValueError("the lengths aren't the same")
        # If I didn't have problem with types or other is a single number, then do the addition
        else:
            return MySeries([self.series[i] * other[i] for i in range(len(self.series))])

    def __imul__(self, other):
        return MySeries.__mul__(self, other)

    def __set_series(self, series):
        if isinstance(series, Iterable) and not(isinstance(series, (str, dict))):
            if self.__is_returns:
                return list(series)
            else:
                return MySeries.__ret(list(series))
        else:
            raise TypeError("the input series isn't an acceptable type of iterable")

    @classmethod
    def __ret(cls, series):
        returns = []
        for i in range(len(series) - 1):
            returns.append(series[i + 1] / series[i] - 1)
        return returns

    def avg_ret(self):
        return sum(self.series) / len(self.series)

    def standard_deviation(self):
        return stdev(self.series)

    def max_drawdown(self, log_to_console= False):
        """"\nAverage between the global max of the series and the following local min value after the drop."""
        global lo
        hi = max(self.series)
        idx = 0
        check_min = False
        for i in self.series:
            if i == hi:  # if I reach the max, then I look for the first following local min
                check_min = True

            if check_min:
                if (len(self.series) - 1 > idx + 2) and (self.series[idx + 2] > self.series[idx + 1]):
                    lo = self.series[idx + 1]
                    break
                elif len(self.series) - 1 == idx + 2:
                    if self.series[idx + 2] <= self.series[idx + 1]:
                        lo = self.series[idx + 2]
                        break
                    else:
                        lo = self.series[idx + 1]
                        break
                elif len(self.series) - 1 == idx + 1:
                    lo = self.series[idx + 1]
                    break
                elif len(self.series) - 1 < idx + 1:
                    lo = None

            idx += 1

        # a little summary
        if lo:
            if log_to_console is True:
                return print('\nmax: {0}, local min: {1}, max_drawdown: {2}'.format(hi, lo, (hi + lo) / 2))
            else:
                return (hi + lo) / 2
        else:
            return None

    def calmar_ratio(self):
        max_drawdown = MySeries.max_drawdown(self, log_to_console=False)
        if max_drawdown:
            return MySeries.avg_ret(self) / max_drawdown
        else:
            return None

    def sharpe_ratio(self, rf= None, rf_is_returns=True):
        # I set the rf=0 if the user didn't provide one
        if not rf:
            rf = [0 for i in range(len(self.series))]
        else:
            rf = rf if rf_is_returns else MySeries.__ret(list(rf))
        # Compute the Asset's extra-returns
        exc_ret = []
        for i in range(len(self.series)):
            exc_ret.append(self.series[i] - rf[i])
        # exc_ret = [(self.series[i] - rf[i]) for i in range(len(self.series))]
        # with small series it seems to be faster, not the same with long series
        return mean(exc_ret) / stdev(self.series)
