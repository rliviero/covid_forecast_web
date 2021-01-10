import pandas as pd
import streamlit as st
from datetime import date, datetime, timedelta
from covid_data import get_covid_world_data, transform_covid_data, write_covid_file
from covid_cleansing import get_last_non_zero
from covid_forecast import calc_forecast, exp_func, lin_func, logi_func, gauss_func
from timeit import default_timer as timer

# Constants

DAYS_BACK = 60

start = timer()
covid_world_orig, source_date = get_covid_world_data(force_use='file')
print(f"loaded data from file as of {source_date} in {round(timer() - start,2)} seconds")

covid_world = transform_covid_data(covid_world_orig)

covid_world['cases_14d'] = covid_world['cases_14_days_per10K'] * (covid_world['popData2019'] / 100000)

all_countries_ordered = covid_world.country.unique().tolist()
primary_countries = ['Switzerland', 'Germany', 'Italy', 'France', 'Austria', 'Spain', 'Sweden', 'United Kingdom',
                     'United States']
all_countries = list(dict.fromkeys(primary_countries + all_countries_ordered))

# General page layout

st.set_page_config(page_title="COVID-19 Forcast", layout="wide")
st.write("# COVID-19 Forecast")
st.write(
    f"Calculate your own forecast of the **COVID-19** development. Solution provided by Roberto Liviero, data by [Our World in Data](https://ourworldindata.org/coronavirus-data) as of {source_date}.")
columns = st.beta_columns(2)

countries = ['Switzerland', 'Germany']
countries[0] = columns[0].selectbox("1. Country:", all_countries, index=0)
countries[1] = columns[1].selectbox("2. Country:", all_countries, index=1)

if countries[0] == countries[1]:
    st.warning('Please choose two different countries.')
    st.stop()

covid_countries = pd.concat([covid_world.loc[covid_world['country'] == country].loc[:get_last_non_zero(
    covid_world.loc[covid_world['country'] == country]['cases']), ] for country in countries])

# Sidebar

st.sidebar.header('User Input Parameters')

# todo: find correct min and max start and end date

start_date = st.sidebar.date_input(label="Start date:", value=(datetime.today() - timedelta(days=DAYS_BACK)).date(),
                                   min_value=covid_countries.index.min().to_pydatetime(),
                                   max_value=covid_countries.index.max().to_pydatetime())

end_date = st.sidebar.date_input(label="End date:", value=(covid_countries.index.max().to_pydatetime()).date(),
                                 min_value=start_date, max_value=covid_countries.index.max().to_pydatetime())

forecast_days = st.sidebar.slider(label="Forecast days:", value=14, min_value=0, max_value=21)

per_10K = st.sidebar.checkbox("Per 100'000 inhabitants", True)

functions = {"Exponential": exp_func, "Linear": lin_func, "Logistic": logi_func, "Gaussian": gauss_func}

auto_func_calc = st.sidebar.checkbox("Automatic forecast", True)

if auto_func_calc:
    selected_functions = functions.keys()
else:
    selected_functions = []
    st.sidebar.write("Forecast functions:")
    for function in functions:
        if st.sidebar.checkbox(function, True):
            selected_functions.append(function)

# Display

indicators = {"Cases": 'cases', "Cumulative Cases for 14 days": 'cases_14d', "Deaths": 'deaths'}

add_title = ""

for index, country in enumerate(countries):
    covid_sample = covid_countries.loc[covid_countries['country'] == country]
    popData2019 = covid_sample['popData2019'].iloc[0]

    for indicator in indicators:
        covid_sample_ind = covid_sample.loc[start_date:end_date, indicators[indicator]]

        if per_10K:
            covid_sample_ind = covid_sample_ind.apply(lambda x: x / (popData2019 / 100000))
            add_title = " per 100'000 inhabitants"

        covid_forecast = covid_sample_ind.reindex(
            pd.date_range(start=start_date, end=end_date + timedelta(days=forecast_days), freq='D'))

        df = covid_forecast.to_frame()

        residuals = {}
        for function in selected_functions:
            func = functions[function]
            df_forecast_func, residuals[func] = calc_forecast(covid_sample_ind, covid_forecast, func)
            if not df_forecast_func.isnull().values.any():
                df[function] = df_forecast_func

        if auto_func_calc and residuals:
            best_fit_func = min(residuals, key=residuals.get)
            for function in selected_functions:
                if functions[function] == best_fit_func:
                    df.rename(columns={function: 'Forecast'}, inplace=True)
                else:
                    if function in df:
                        del df[function]

        df.rename(columns={indicators[indicator]: indicators[indicator].capitalize()}, inplace=True)

        with columns[index]:
            st.write("**{}{}**".format(indicator, add_title))
            st.line_chart(df)

start = timer()
covid_world_orig, new_source_date = get_covid_world_data(force_use='http')
print(f"loaded data from http as of {source_date} in {round(timer() - start,2)} seconds")

if new_source_date > source_date:
    start = timer()
    write_covid_file(covid_world_orig, new_source_date)
    print(f"written data as of {source_date} in {round(timer() - start,2)} seconds")

#st.experimental_rerun()
