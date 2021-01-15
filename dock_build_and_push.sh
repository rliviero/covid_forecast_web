#docker buildx build --platform linux/amd64 --tag covid_forecast_web:latest .
docker buildx build --target app --platform linux/amd64 --tag covid_forecast_web:latest .
docker tag covid_forecast_web:latest roberto3014/covid_forecast_web:latest
docker push roberto3014/covid_forecast_web:latest
#docker run -p 80:80 roberto3014/covid_forecast_web:latest
az login
az container restart --resource-group covid_forcast_web_rg --name covid-forecast-web-ct
