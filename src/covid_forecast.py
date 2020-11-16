import pandas as pd
import numpy as np
from scipy.optimize import curve_fit


def lin_func(x, a, b):
    return a + b * x


def exp_func(x, a, b):
    return a * np.exp(b * x)


def logi_func(x, L, x0, k):
    return L / (1 + np.exp(-1 * k * (x - x0)))


def gauss_func(x, a, x0, sigma):
    return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))


initials = {lin_func: (0, 5.0), exp_func: (3, 0.001), logi_func: (2, 2.5e-4, 200), gauss_func: (100, 60, 10)}


def calc_forecast(df_sample, df_forecast, func):
    x = np.arange(df_sample.index.size)
    y = df_sample

    if func == gauss_func:
        mean = sum(x * y) / sum(y)
        sigma = np.sqrt(sum(y * (x - mean) ** 2) / sum(y))
        initials[gauss_func] = [max(y), mean, sigma]

    if func == logi_func:
        initials[logi_func] = [max(y), max(x) / 2, 0.1]

    try:
        popt, pcov = curve_fit(func, x, y, p0=initials[func], maxfev=20000)
        func_y = func(np.arange(df_forecast.index.size), *popt)

    except RuntimeError:
        func_y = np.empty(df_forecast.index.size)
        func_y = func_y.fill(np.NaN)

    return pd.DataFrame(func_y, columns=['forecast'], index=df_forecast.index)
