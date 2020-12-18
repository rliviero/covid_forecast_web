import pandas as pd
import datetime as dt

from urllib.request import urlopen
from urllib.request import Request
from dateutil.parser import parse as parsedate
import os


def get_covid_world_data():
    # read and check source

    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = base_dir + "/owid-covid.world.csv"

    request = Request(url)
    response = urlopen(request)
    url_datetime = parsedate(response.headers['Date']).astimezone()

    if os.path.isfile(file_path) and dt.datetime.fromtimestamp(os.path.getmtime(file_path)).astimezone() > url_datetime:
        source = file_path
        source_date_format = "%Y-%m-%d"
    else:
        source = url
        source_date_format = "%Y-%m-%d"

    covid_world = pd.read_csv(source, parse_dates=['date'])

    if source == url:
        covid_world.to_csv(file_path)

    # columns: iso_code,continent,location,date,total_cases,new_cases,new_cases_smoothed,total_deaths,new_deaths,new_deaths_smoothed,total_cases_per_million,new_cases_per_million,new_cases_smoothed_per_million,total_deaths_per_million,new_deaths_per_million,new_deaths_smoothed_per_million,reproduction_rate,icu_patients,icu_patients_per_million,hosp_patients,hosp_patients_per_million,weekly_icu_admissions,weekly_icu_admissions_per_million,weekly_hosp_admissions,weekly_hosp_admissions_per_million,new_tests,total_tests,total_tests_per_thousand,new_tests_per_thousand,new_tests_smoothed,new_tests_smoothed_per_thousand,positive_rate,tests_per_case,tests_units,total_vaccinations,total_vaccinations_per_hundred,stringency_index,population,population_density,median_age,aged_65_older,aged_70_older,gdp_per_capita,extreme_poverty,cardiovasc_death_rate,diabetes_prevalence,female_smokers,male_smokers,handwashing_facilities,hospital_beds_per_thousand,life_expectancy,human_development_index

    covid_world.rename(
        columns={'new_cases_smoothed': 'cases', 'new_deaths_smoothed': 'deaths', 'location': 'country',
                 'population': 'popData2019'},
        inplace=True)

    covid_world['cases_14_days_per10K'] = covid_world['cases'].rolling(14).sum() / (covid_world['popData2019'] / 100000)

    covid_world.set_index('date', inplace=True)

    return covid_world[['country', 'cases', 'deaths', 'popData2019', 'cases_14_days_per10K']]

# Test

if __name__ == "__main__":

    from timeit import  default_timer as timer

    start = timer()
    df = get_covid_world_data()
    print(f"loaded data in {timer()-start} seconds")
    print(df.index.dtype)
    df_ch = df.loc[df['country'] == "Switzerland"]
    print(df_ch)

    import datetime as dt
    end_date = (dt.datetime.today() - dt.timedelta(days=1)).date()
    start_date = (dt.datetime.today() - dt.timedelta(days=21)).date()
    print(df_ch.loc[start_date:end_date, 'cases'])



