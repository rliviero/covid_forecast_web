import pandas as pd
import numpy as np
from scipy.optimize import curve_fit


def lin_func(x, a, b):
    return a + b * x


def exp_func(x, a, b):
    return a * np.exp(b * x)


#def logi_func(x, l, c, k):
#    return l / (1 + c * np.exp(-k * x))


def logi_func(x, b0, k, s):
    return s * 1 / (1 + np.exp(-1 * k * s * x) * (s / b0 - 1))


#params = curve_fit(lgt_func, x, covid_sample, p0=[2, 2.5e-4, 200],
#                   maxfev=10000)  # bounds=([0, 1e-5, covid_sample[-1]], [covid_sample[-1], 0.9, 100000])



initials = {lin_func: (0, 5.0), exp_func: (3, 0.001), logi_func: (2, 2.5e-4, 200)}
# bounds for a,b: (a min, b min), a max, b max)
bounds = {lin_func: ((0, -np.inf), (np.inf, np.inf)), exp_func: ((0, -np.inf), (np.inf, np.inf)),
          logi_func: ((0, -np.inf, -np.inf), (np.inf, np.inf, np.inf))}


def calc_forecast(df_sample, df_forecast, func):
    params = curve_fit(func, np.arange(df_sample.index.size), df_sample, p0=initials[func], bounds=bounds[func], maxfev=10000)
    func_params = params[0]
    print(func)
    print(func_params)
    #func_y = func(np.arange(df_forecast.index.size), func_params[0], func_params[1])
    func_y = func(np.arange(df_forecast.index.size), *func_params)
    return pd.DataFrame(func_y, columns=['forecast'], index=df_forecast.index)


