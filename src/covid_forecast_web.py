import pandas as pd
import streamlit as st
from datetime import date, datetime, timedelta
from covid_data import get_covid_world_data
from covid_forecast import calc_forecast, exp_func, lin_func

covid_world = get_covid_world_data()
all_countries_ordered = covid_world.country.unique().tolist()
primary_countries = ['Switzerland', 'Germany', 'Italy', 'France', 'Austria', 'Spain', 'Sweden']
all_countries = list(dict.fromkeys(primary_countries + all_countries_ordered))

# General page layout

st.beta_set_page_config(page_title="COVID-19 Forcast", layout="wide")
#header = st.beta_container()
columns = st.beta_columns(2)
#footer = st.beta_container()

st.write("# COVID-19 Forecast\nCalculate your own forecast of the **COVID-19** development")

columns = st.beta_columns(2)

st.sidebar.header('User Input Parameters')
countries = ['Switzerland', 'Germany']
countries[0] = st.sidebar.selectbox("1. Country:", all_countries, index=0)
countries[1] = st.sidebar.selectbox("2. Country:", all_countries, index=1)

indicators = {"Cases": 'cases', "Deaths": 'deaths', "Cases for 14 days per 100'000": 'cases_14_days_per10K'}
indicator = st.sidebar.selectbox("Indicator:", list(indicators.keys()), 2)

covid_sample = covid_world.loc[covid_world['country'].isin(countries)].iloc[::-1]

start_date = st.sidebar.date_input(label="Start date:", value=datetime.today() - timedelta(days=60),
                                   min_value=covid_sample.index.min().to_pydatetime(),
                                   max_value=covid_sample.index.max().to_pydatetime())

end_date = st.sidebar.date_input(label="End date:", value=covid_sample.index.max().to_pydatetime(),
                                 min_value=start_date, max_value=covid_sample.index.max().to_pydatetime())

forecast_days = st.sidebar.slider(label="Forecast days:", value=7, min_value=0, max_value=21)

functions = {"Linear": lin_func, "Exponential": exp_func}
function = st.sidebar.radio("Forecast function:", ["Linear", "Exponential"])

i=0
for country in countries:
    covid_sample = covid_world.loc[covid_world['country'] == country].iloc[::-1]
    covid_sample = covid_sample.loc[start_date:end_date, indicators[indicator]]
    covid_forecast = covid_sample.reindex(
        pd.date_range(start=start_date, end=end_date + timedelta(days=forecast_days), freq='D'))

    df_forecast = calc_forecast(covid_sample, covid_forecast, functions[function])
    df = covid_sample.to_frame()
    df = pd.merge(df_forecast, df, how='outer', left_index=True, right_index=True)

    with columns[i]:
        st.write("** {} **".format(country))
        st.line_chart(df)

    i += 1

st.write(">*Data provided by [European Centre for Disease Prevention and Control](https://opendata.ecdc.europa.eu)*")