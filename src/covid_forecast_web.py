import pandas as pd
import streamlit as st
from datetime import date, datetime, timedelta
from covid_data import get_covid_world_data
from covid_cleansing import get_last_non_zero
from covid_forecast import calc_forecast, exp_func, lin_func, logi_func, gauss_func

# Get and prepare data

covid_world = get_covid_world_data()
covid_world['cases_14d'] = covid_world['cases_14_days_per10K'] * (covid_world['popData2019'] / 100000)

all_countries_ordered = covid_world.country.unique().tolist()
primary_countries = ['Switzerland', 'Germany', 'Italy', 'France', 'Austria', 'Spain', 'Sweden', 'United_Kingdom',
                     'United_States_of_America']
all_countries = list(dict.fromkeys(primary_countries + all_countries_ordered))

# General page layout

st.set_page_config(page_title="COVID-19 Forcast", layout="wide")
st.write("# COVID-19 Forecast")
st.write(
    "Calculate your own forecast of the **COVID-19** development. Solution provided by Roberto Liviero, data by [ECDC](https://opendata.ecdc.europa.eu).")
columns = st.beta_columns(2)

countries = ['Switzerland', 'Germany']
countries[0] = columns[0].selectbox("1. Country:", all_countries, index=0)
countries[1] = columns[1].selectbox("2. Country:", all_countries, index=1)

if countries[0] == countries[1]:
    st.warning('Please choose two different countries.')
    st.stop()

covid_countries = pd.concat([covid_world.loc[covid_world['country'] == country].iloc[::-1].loc[:get_last_non_zero(
    covid_world.loc[covid_world['country'] == country].iloc[::-1]['cases']), ] for country in countries])

# Sidebar

st.sidebar.header('User Input Parameters')

# todo: find correct min and max start and end date

start_date = st.sidebar.date_input(label="Start date:", value=datetime.today() - timedelta(days=60),
                                   min_value=covid_countries.index.min().to_pydatetime(),
                                   max_value=covid_countries.index.max().to_pydatetime())

end_date = st.sidebar.date_input(label="End date:", value=covid_countries.index.max().to_pydatetime(),
                                 min_value=start_date, max_value=covid_countries.index.max().to_pydatetime())

forecast_days = st.sidebar.slider(label="Forecast days:", value=7, min_value=0, max_value=21)
roll_avg_window = st.sidebar.slider(label="Rolling average window:", value=7, min_value=2, max_value=14)

per_10K = st.sidebar.checkbox("Per 100'000 inhabitants", True)

functions = {"Exponential": exp_func, "Linear": lin_func, "Logistic": logi_func, "Gaussian": gauss_func}

st.sidebar.write("Forecast functions:")
selected_functions = []
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
        df['Roll. avg'] = df[indicators[indicator]].rolling(window=roll_avg_window).mean()

        for function in selected_functions:
            df_forecast_func = calc_forecast(covid_sample_ind, covid_forecast, functions[function])
            if not df_forecast_func.isnull().values.any():
                df[function] = df_forecast_func

        df.rename(columns={indicators[indicator]: indicators[indicator].capitalize()}, inplace = True)

        with columns[index]:
            st.write("**{}{}**".format(indicator, add_title))
            st.line_chart(df)
