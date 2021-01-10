from covid_data import get_covid_world_data
from time import sleep

INTERVAL = 60

while True:
    df = get_covid_world_data()
    #print(len(df))
    sleep(INTERVAL)