docker build --tag covid_forecast_web:latest .
docker tag covid_forecast_web:latest roberto3014/covid_forecast_web:latest
docker push roberto3014/covid_forecast_web:latest
#docker run -p 80:80 roberto3014/covid_forecast_web:latest