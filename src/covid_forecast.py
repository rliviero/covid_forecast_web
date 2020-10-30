import pandas as pd
import numpy as np
from scipy.optimize import curve_fit


def lin_func(x, a, b):
    return a + b * x

def exp_func(x, a, b):
    return a * np.exp(b * x)

def calc_forecast(df_sample, df_forecast, func):
    params = curve_fit(func, np.arange(df_sample.index.size), df_sample, p0=(1, 0.001))
    func_params = params[0]
    func_y = func(np.arange(df_forecast.index.size), func_params[0], func_params[1])
    return pd.DataFrame(func_y, columns=['forecast'], index=df_forecast.index)


