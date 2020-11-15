import pandas as pd

def get_last_non_zero(serie):
    return serie[serie != 0].index[-1]
