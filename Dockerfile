FROM python:3.8-slim

EXPOSE 80

WORKDIR /app
COPY requirements.txt .
COPY config.toml .
COPY credentials.toml .
COPY src/covid_data.py .
COPY src/covid_cleansing.py .
COPY src/covid_forecast.py .
COPY src/covid_forecast_web.py .
COPY src/owid-covid.world.csv .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir ~/.streamlit
RUN cp config.toml ~/.streamlit/config.toml
RUN cp credentials.toml ~/.streamlit/credentials.toml

ENV GIT_PYTHON_REFRESH=quiet
ENTRYPOINT ["streamlit", "run"]
CMD ["covid_forecast_web.py"]
