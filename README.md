# HotelAzura-ModeloReservas

API para entrenar y consultar un modelo predictivo de reservas del sistema Hotel Azura.

## Tecnologías

- Python
- FastAPI
- Pandas
- Scikit-learn
- Joblib

## Dataset

El modelo utiliza un dataset histórico mensual ubicado en:

```text
data/dataset_us73_prediccion_mensual.csv

El modelo utiliza regresión Ridge para estimar la cantidad mensual de reservas a partir del año y el mes. 
El sistema transforma los datos históricos en una serie temporal mensual, permitiendo aprender tanto la tendencia de crecimiento por año como los patrones estacionales por mes.

## Ejecutar api

Comando: uvicorn app.main:app --reload