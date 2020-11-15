FROM python:3.7.2-slim

EXPOSE 80

WORKDIR /app
COPY requirements.txt .
COPY config.toml .
COPY credentials.toml .
COPY src/covid_data.py .
COPY src/covid_cleansing.py .
COPY src/covid_forecast.py .
COPY src/covid_forecast_web.py .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir ~/.streamlit
RUN cp config.toml ~/.streamlit/config.toml
RUN cp credentials.toml ~/.streamlit/credentials.toml

ENTRYPOINT ["streamlit", "run"]
CMD ["covid_forecast_web.py"]
