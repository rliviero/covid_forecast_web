import pandas as pd
import datetime as dt


from urllib.request import urlopen
from urllib.request import Request
from dateutil.parser import parse as parsedate
import os

def get_covid_world_data():

    # read and check source

    url = "https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = base_dir + "/covid.world.csv"

    request = Request(url)
    response = urlopen(request)
    url_datetime = parsedate(response.headers['Last-Modified']).astimezone()

    if os.path.isfile(file_path) and dt.datetime.fromtimestamp(os.path.getmtime(file_path)).astimezone() > url_datetime:
        source = file_path
        source_date_format = "%Y-%m-%d"
    else:
        source = url
        source_date_format = "%d/%m/%Y"

    covid_world = pd.read_csv(source,
                              index_col=0, parse_dates=['dateRep'],
                              date_parser=lambda x: dt.datetime.strptime(x, source_date_format).date())

    if source == url:
        covid_world.to_csv(file_path)

    covid_world.rename(columns={'countriesAndTerritories': 'country',
                                'Cumulative_number_for_14_days_of_COVID-19_cases_per_100000': 'cases_14_days_per10K'},
                       inplace=True)

    covid_world.index.rename('date', inplace=True)

    return covid_world[['country', 'continentExp', 'cases', 'deaths', 'popData2019', 'cases_14_days_per10K']]

