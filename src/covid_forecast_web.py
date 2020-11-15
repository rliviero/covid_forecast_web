import pandas as pd
import streamlit as st
from datetime import date, datetime, timedelta
from covid_data import get_covid_world_data
from covid_forecast import calc_forecast, exp_func, lin_func, logi_func

# Get and prepare data

covid_world = get_covid_world_data()
all_countries_ordered = covid_world.country.unique().tolist()
primary_countries = ['Switzerland', 'Germany', 'Italy', 'France', 'Austria', 'Spain', 'Sweden']
all_countries = list(dict.fromkeys(primary_countries + all_countries_ordered))

# General page layout

st.set_page_config(page_title="COVID-19 Forcast", layout="wide")
st.write("# COVID-19 Forecast")
st.write("Calculate your own forecast of the **COVID-19** development. Solution provided by Roberto Liviero, data by [ECDC](https://opendata.ecdc.europa.eu).")
columns = st.beta_columns(2)

# Sidebar

st.sidebar.header('User Input Parameters')
countries = ['Switzerland', 'Germany']
countries[0] = columns[0].selectbox("1. Country:", all_countries, index=0)
countries[1] = columns[1].selectbox("2. Country:", all_countries, index=1)

covid_sample = covid_world.loc[covid_world['country'].isin(countries)].iloc[::-1]

start_date = st.sidebar.date_input(label="Start date:", value=datetime.today() - timedelta(days=60),
                                   min_value=covid_sample.index.min().to_pydatetime(),
                                   max_value=covid_sample.index.max().to_pydatetime())

end_date = st.sidebar.date_input(label="End date:", value=covid_sample.index.max().to_pydatetime(),
                                 min_value=start_date, max_value=covid_sample.index.max().to_pydatetime())

forecast_days = st.sidebar.slider(label="Forecast days:", value=7, min_value=0, max_value=21)

functions = {"Exponential": exp_func, "Linear": lin_func, "Logistic": logi_func}
function = st.sidebar.radio("Forecast function:", ["Exponential", "Linear", "Logistic"])

# Display

indicators = {"Cases for 14 days per 100'000": 'cases_14_days_per10K', "Cases": 'cases', "Deaths": 'deaths', }

for index, country in enumerate(countries):
    covid_sample = covid_world.loc[covid_world['country'] == country].iloc[::-1]
    for indicator in indicators:
        covid_sample_ind = covid_sample.loc[start_date:end_date, indicators[indicator]]
        covid_forecast = covid_sample_ind.reindex(
            pd.date_range(start=start_date, end=end_date + timedelta(days=forecast_days), freq='D'))

        df_forecast = calc_forecast(covid_sample_ind, covid_forecast, functions[function])
        df = covid_sample_ind.to_frame()
        df = pd.merge(df_forecast, df, how='outer', left_index=True, right_index=True)

        with columns[index]:
            st.write("**{}**".format(indicator))
            st.line_chart(df)


