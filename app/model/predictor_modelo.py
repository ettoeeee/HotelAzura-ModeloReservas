import json

import joblib
import pandas as pd

from app.core.config import MODEL_PATH, METADATA_PATH, MESES_NOMBRE


def cargar_modelo_y_metadata():
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError("El modelo aún no ha sido generado.")

    modelo = joblib.load(MODEL_PATH)

    with open(METADATA_PATH, "r", encoding="utf-8") as archivo:
        metadata = json.load(archivo)

    return modelo, metadata


def predecir_meses(meses_a_predecir):
    modelo, metadata = cargar_modelo_y_metadata()

    anio_base = metadata["anio_base"]

    filas = []

    for item in meses_a_predecir:
        anio = item["anio"]
        mes = item["mes"]
        indice_tiempo = ((anio - anio_base) * 12) + (mes - 1)

        filas.append({
            "anio": anio,
            "mes": mes,
            "indice_tiempo": indice_tiempo
        })

    df_prediccion = pd.DataFrame(filas)

    X = df_prediccion[["indice_tiempo", "mes"]]
    resultados = modelo.predict(X)

    predicciones = []

    for item, valor in zip(meses_a_predecir, resultados):
        reservas_estimadas = max(0, int(round(valor)))

        predicciones.append({
            "anio": item["anio"],
            "mes": item["mes"],
            "nombreMes": MESES_NOMBRE[item["mes"]],
            "reservasEstimadas": reservas_estimadas
        })

    return predicciones, metadata