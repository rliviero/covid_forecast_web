from urllib.request import urlopen, Request
from dateutil.parser import parse as parsedate
import datetime as dt
import os
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = base_dir + "/owid-covid.world.csv"
url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"


def get_covid_http_handle():
    request = Request(url)
    response = urlopen(request)
    url_datetime = parsedate(response.headers['Date']).astimezone()
    return response, url_datetime


def get_covid_file_handle():
    if os.path.isfile(file_path):
        file = open(file_path, "r")
        file_datetime = dt.datetime.fromtimestamp(os.path.getmtime(file_path)).astimezone()
        return file, file_datetime
    else:
        return None, None


def write_covid_file(df, source_date):
    df.to_csv(file_path)
    # we set modification date/time to source date/time to preserve this information
    os.utime(file_path, (source_date.timestamp(), source_date.timestamp()))


# force_use ('file' or 'http') is primarly for testing
# return a handle, date of data and type of source
def get_covid_source(force_use=None):

    if force_use == 'file':
        file, file_datetime = get_covid_file_handle()
        if file:
            return file, file_datetime
        else:
            return get_covid_http_handle()

    if force_use == 'http':
        return get_covid_http_handle()

    # return http source if newer, else return file
    response, url_datetime = get_covid_http_handle()
    file, file_datetime = get_covid_file_handle()
    if file and file_datetime >= url_datetime:
        return file, file_datetime
    else:
        return response, url_datetime


def get_covid_world_data(force_use=None):
    # read and check source

    source, source_date = get_covid_source(force_use)

    covid_world = pd.read_csv(source, parse_dates=['date'])

    return covid_world, source_date


def transform_covid_data(covid_world):
    # columns: iso_code,continent,location,date,total_cases,new_cases,new_cases_smoothed,total_deaths,new_deaths,new_deaths_smoothed,total_cases_per_million,new_cases_per_million,new_cases_smoothed_per_million,total_deaths_per_million,new_deaths_per_million,new_deaths_smoothed_per_million,reproduction_rate,icu_patients,icu_patients_per_million,hosp_patients,hosp_patients_per_million,weekly_icu_admissions,weekly_icu_admissions_per_million,weekly_hosp_admissions,weekly_hosp_admissions_per_million,new_tests,total_tests,total_tests_per_thousand,new_tests_per_thousand,new_tests_smoothed,new_tests_smoothed_per_thousand,positive_rate,tests_per_case,tests_units,total_vaccinations,total_vaccinations_per_hundred,stringency_index,population,population_density,median_age,aged_65_older,aged_70_older,gdp_per_capita,extreme_poverty,cardiovasc_death_rate,diabetes_prevalence,female_smokers,male_smokers,handwashing_facilities,hospital_beds_per_thousand,life_expectancy,human_development_index

    covid_world.rename(
        columns={'new_cases_smoothed': 'cases', 'new_deaths_smoothed': 'deaths', 'location': 'country',
                 'population': 'popData2019'},
        inplace=True)

    covid_world['cases_14_days_per10K'] = covid_world['cases'].rolling(14).sum() / (covid_world['popData2019'] / 100000)

    covid_world.set_index('date', inplace=True)

    return covid_world[['country', 'cases', 'deaths', 'popData2019', 'cases_14_days_per10K']].copy()


# Test

if __name__ == "__main__":
    import datetime as dt
    from timeit import default_timer as timer

    # make sure it get the newest data trough a request
    os.utime(file_path, (dt.datetime.now().timestamp(), dt.datetime(2019, 1, 1, 12, 0, 0).timestamp()))
    start = timer()
    df, date = get_covid_world_data()
    print(f"loaded data as of {date} in {timer() - start} seconds")

    # get from file
    os.utime(file_path, (dt.datetime.now().timestamp(), dt.datetime.now().timestamp()))
    start = timer()
    df, date = get_covid_world_data()
    print(f"loaded data as of {date} in {timer() - start} seconds")

    df = transform_covid_data(df)

    print(df.index.dtype)
    df_ch = df.loc[df['country'] == "Switzerland"]
    print(df_ch.head())

    end_date = (dt.datetime.today() - dt.timedelta(days=1)).date()
    start_date = (dt.datetime.today() - dt.timedelta(days=21)).date()
    print(df_ch.loc[start_date:end_date, 'cases'].head())
